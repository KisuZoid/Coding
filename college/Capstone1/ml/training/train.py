"""Research training entrypoint for the baseline-vs-hybrid ablation (spec v3).

Supports the controlled comparison required by
``docs/architecture/cnn-transformer-segmentation.md``:

    --model baseline  -> ResNet34UNet   (pretrained ResNet34 + shared decoder)
    --model hybrid    -> HybridSegmentation (ResNet34 + bottleneck Transformer
                                             + additive fusion + same decoder)

Both architectures run through the *same* pipeline and differ only in the
Transformer/fusion component:

    dataset -> dataloader -> Dice+Focal loss -> AdamW (2 LR groups)
    -> 5-epoch warmup + cosine decay -> EMA -> validation -> checkpoint

Training protocol (locked in the spec, Sections 8-16):

- effective batch size 4 (physical batch x gradient accumulation)
- mixed precision + GradScaler, gradient accumulation
- encoder BN running statistics frozen for small physical batches
- EMA weights used for validation, checkpoint selection and the saved artefact
- class-aware sampling on the training split only
- best-checkpoint selection on validation foreground mIoU
- early stopping after 10 epochs without validation mIoU improvement
- run record + experiment registry for reproducibility

Legacy runnable models ``cardd_unet`` / ``cardd_hybrid`` remain selectable
(their forward returns a single logit tensor; the shared pipeline treats them
as main-only outputs).

Run inside the `ai` conda environment:

    python ml/training/train.py \\
        --data-root datasets/CarDD_COCO \\
        --model baseline --label baseline_r34

    python ml/training/train.py \\
        --data-root datasets/CarDD_COCO \\
        --model hybrid --label hybrid_ct
"""

from __future__ import annotations

import argparse
import contextlib
import json
import math
import subprocess
import sys
import time
from collections.abc import Iterator, Sized
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

import torch
from torch import nn

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from ml.evaluation.metrics import (  # noqa: E402
    confusion_matrix,
    mean_dice,
    mean_iou,
    per_class_dice,
    per_class_iou,
)
from ml.models.cardd_hybrid import CarddHybrid  # noqa: E402
from ml.models.cardd_unet import CarddUNet  # noqa: E402
from ml.models.hybrid_segmentation import HybridSegmentation  # noqa: E402
from ml.models.resnet34_unet import ResNet34UNet  # noqa: E402
from ml.training.cardd_dataset import (  # noqa: E402
    CarddInstanceSegDataset,
    collate_seg,
)
from ml.training.class_stats import get_train_class_stats  # noqa: E402
from ml.training.ema import EMA  # noqa: E402
from ml.training.loss import (  # noqa: E402
    ClassWeights,
    aggregate_targets,
    dice_focal_loss,
)

LEGACY_ARCHES = {"cardd_unet", "CarddUNet", "cardd_hybrid", "CarddHybrid"}


@dataclass
class TrainingConfig:
    """Reproducible experiment settings (recorded verbatim per run)."""

    data_root: str
    split: str = "train2017"
    model_arch: str = "hybrid_segmentation"
    epochs: int = 60
    batch_size: int = 2
    grad_accum: int = 2
    base: int = 0
    lr_backbone: float = 1e-4
    lr_head: float = 3e-4
    weight_decay: float = 1e-4
    warmup_epochs: int = 5
    min_lr: float = 1e-6
    patience: int = 10
    ema_decay: float = 0.999
    train_limit: int | None = None
    val_limit: int | None = None
    augment_train: bool = True
    class_sampling: bool = True
    pretrained: bool = True
    pretrained_path: str | None = None
    freeze_encoder_bn: bool = True
    checkpoint_every: int = 5
    seed: int = 0
    num_workers: int = 0
    experiment_label: str = "research"


class WarmupCosineLR:
    """Linear warmup followed by cosine decay to a minimum LR (spec 11).

    Applied once per epoch; ``step(epoch)`` writes the exact LR into each
    parameter group so the backbone and head groups decay to their own floors.
    """

    def __init__(
        self, optimizer: torch.optim.Optimizer, warmup_epochs: int, total_epochs: int, min_lr: float
    ) -> None:
        self.optimizer = optimizer
        self.warmup_epochs = max(1, warmup_epochs)
        self.total_epochs = max(self.warmup_epochs + 1, total_epochs)
        self.min_lr = max(0.0, min_lr)
        self._peak_lrs = [float(group["lr"]) for group in optimizer.param_groups]

    def epoch_lrs(self, epoch: int) -> list[float]:
        if epoch < self.warmup_epochs:
            factor = (epoch + 1) / self.warmup_epochs
            return [peak * factor for peak in self._peak_lrs]
        fraction = (epoch - self.warmup_epochs) / max(1, self.total_epochs - self.warmup_epochs)
        cosine = 0.5 * (1.0 + math.cos(math.pi * min(1.0, fraction)))
        return [self.min_lr + (peak - self.min_lr) * cosine for peak in self._peak_lrs]

    def step(self, epoch: int) -> None:
        for group, lr in zip(self.optimizer.param_groups, self.epoch_lrs(epoch), strict=True):
            group["lr"] = lr

    def get_last_lr(self) -> list[float]:
        return [float(group["lr"]) for group in self.optimizer.param_groups]


def build_model(
    arch: str,
    num_classes: int,
    base: int,
    pretrained: bool,
    pretrained_path: str | None,
) -> nn.Module:
    arch_l = arch.lower()
    if arch_l in {"resnet34_unet", "baseline"}:
        return ResNet34UNet(
            num_classes=num_classes, pretrained=pretrained, weights_path=pretrained_path
        )
    if arch_l in {"hybrid_segmentation", "hybrid"}:
        return HybridSegmentation(
            num_classes=num_classes, pretrained=pretrained, weights_path=pretrained_path
        )
    if arch_l == "cardd_unet":
        return CarddUNet(num_classes=num_classes, base=base)
    if arch_l == "cardd_hybrid":
        return CarddHybrid(num_classes=num_classes, base=base)
    raise ValueError(f"unknown model_arch: {arch}")


def git_revision() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True)
            .strip()
            .splitlines()[0]
        )
    except subprocess.CalledProcessError:
        return "unknown"


def seed_all(seed: int) -> None:
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def build_optimizer(model: nn.Module, config: TrainingConfig) -> torch.optim.Optimizer:
    encoder = getattr(model, "encoder", None)
    backbone_params = list(encoder.parameters()) if isinstance(encoder, nn.Module) else []
    backbone_ids = {id(param) for param in backbone_params}
    other_params = [param for param in model.parameters() if id(param) not in backbone_ids]
    groups: list[dict[str, Any]] = []
    if backbone_params:
        groups.append(
            {
                "params": backbone_params,
                "lr": config.lr_backbone,
                "weight_decay": config.weight_decay,
            }
        )
    groups.append(
        {"params": other_params, "lr": config.lr_head, "weight_decay": config.weight_decay}
    )
    return torch.optim.AdamW(groups)


@contextlib.contextmanager
def _amp_context(use_amp: bool) -> Iterator[None]:
    if use_amp:
        with torch.autocast(device_type="cuda", dtype=torch.float16):
            yield
    else:
        yield


def _freeze_encoder_bn(model: nn.Module) -> None:
    """Freeze ResNet34 BatchNorm running statistics (spec 12, small batches)."""
    encoder = getattr(model, "encoder", None)
    if not isinstance(encoder, nn.Module):
        return
    for child in encoder.modules():
        if isinstance(child, nn.BatchNorm2d):
            child.eval()


def forward_outputs(
    model: nn.Module, images: torch.Tensor
) -> tuple[torch.Tensor, torch.Tensor | None, torch.Tensor | None]:
    out = model(images)
    if isinstance(out, tuple | list):
        main = cast(torch.Tensor, out[0])
        aux1 = out[1] if len(out) > 1 else None
        aux2 = out[2] if len(out) > 2 else None
        return main, aux1, aux2
    return cast(torch.Tensor, out), None, None


def make_train_loader(
    data_root: Path,
    config: TrainingConfig,
    sampler_weights: list[float] | None,
) -> torch.utils.data.DataLoader[Any]:
    ds = CarddInstanceSegDataset(
        data_root,
        split="train2017",
        limit=config.train_limit,
        seed=config.seed,
        augment=config.augment_train,
    )
    sampler: torch.utils.data.Sampler[int] | None = None
    shuffle = True
    if sampler_weights is not None and config.train_limit is None:
        sampler = torch.utils.data.WeightedRandomSampler(
            sampler_weights, num_samples=len(ds), replacement=True
        )
        shuffle = False
    return torch.utils.data.DataLoader(
        ds,
        batch_size=config.batch_size,
        shuffle=shuffle,
        sampler=sampler,
        num_workers=config.num_workers,
        drop_last=False,
        collate_fn=collate_seg,
    )


def make_val_loader(data_root: Path, config: TrainingConfig) -> torch.utils.data.DataLoader[Any]:
    ds = CarddInstanceSegDataset(
        data_root, split="val2017", limit=config.val_limit, seed=config.seed, augment=False
    )
    return torch.utils.data.DataLoader(
        ds,
        batch_size=config.batch_size,
        shuffle=False,
        num_workers=config.num_workers,
        drop_last=False,
        collate_fn=collate_seg,
    )


def train_epoch(
    loader: torch.utils.data.DataLoader[Any],
    model: nn.Module,
    optimizer: torch.optim.Optimizer,
    scaler: Any,
    ema: EMA,
    device: torch.device,
    num_classes: int,
    weights: ClassWeights,
    config: TrainingConfig,
) -> dict[str, float]:
    """One training epoch over the loader (mixed precision + accumulation)."""
    model.train()
    use_amp = scaler is not None

    def _step() -> None:
        if scaler is not None:
            scaler.step(optimizer)
            scaler.update()
        else:
            optimizer.step()
        optimizer.zero_grad(set_to_none=True)
        ema.update(model)

    totals: dict[str, float] = {}
    count = 0
    accum = 0
    fwd_ms = 0.0
    bwd_ms = 0.0
    for batch in loader:
        images = batch["image"].to(device)
        masks = batch["masks"].to(device)
        labels = batch["labels"].to(device)
        if config.freeze_encoder_bn:
            _freeze_encoder_bn(model)

        t0 = time.perf_counter()
        with _amp_context(use_amp):
            main_logits, aux1_logits, aux2_logits = forward_outputs(model, images)
            loss, parts = dice_focal_loss(
                main_logits,
                aux1_logits,
                aux2_logits,
                masks,
                labels,
                num_classes,
                weights,
            )
            loss = loss / float(config.grad_accum)
        t1 = time.perf_counter()
        if scaler is not None:
            scaler.scale(loss).backward()
        else:
            loss.backward()  # type: ignore[no-untyped-call]
        t2 = time.perf_counter()

        fwd_ms += t1 - t0
        bwd_ms += t2 - t1
        accum += 1
        count += 1
        for key, value in parts.items():
            totals[key] = totals.get(key, 0.0) + value
        totals["total"] = totals.get("total", 0.0) + float(loss.item()) * float(config.grad_accum)
        if accum % config.grad_accum == 0:
            _step()
            accum = 0
    if accum > 0:
        _step()

    stats: dict[str, float] = {"n_batches": float(count)}
    stats["total_loss"] = totals.get("total", 0.0) / max(count, 1)
    stats["main_loss"] = totals.get("main", 0.0) / max(count, 1)
    stats["aux1_loss"] = totals.get("aux1", 0.0) / max(count, 1)
    stats["aux2_loss"] = totals.get("aux2", 0.0) / max(count, 1)
    stats["fwd_secs"] = fwd_ms
    stats["bwd_secs"] = bwd_ms
    return stats


@torch.no_grad()
def evaluate(
    loader: torch.utils.data.DataLoader[Any],
    model: nn.Module,
    device: torch.device,
    num_classes: int,
) -> dict[str, Any]:
    """Validation under the EMA weights: per-class + foreground metrics."""
    model.eval()
    conf = torch.zeros(num_classes, num_classes, dtype=torch.long, device=device)
    correct, n_pixels = 0, 0
    for batch in loader:
        images = batch["image"].to(device)
        masks = batch["masks"].to(device)
        labels = batch["labels"].to(device)
        targets = aggregate_targets(masks, labels, num_classes)
        main_logits, _, _ = forward_outputs(model, images)
        pred_classes = main_logits.argmax(dim=1)
        target_classes = targets.argmax(dim=1)
        conf += confusion_matrix(pred_classes, target_classes, num_classes).to(device).long()
        match = pred_classes == target_classes
        correct += int(match.sum())
        n_pixels += int(torch.numel(target_classes))

    conf = conf.cpu()
    per_class = {
        str(c): {"iou": float(v), "dice": float(d)}
        for c, (v, d) in enumerate(zip(per_class_iou(conf), per_class_dice(conf), strict=True))
    }
    return {
        "foreground_miou": mean_iou(conf),
        "foreground_mdice": mean_dice(conf),
        "pixel_accuracy": correct / max(n_pixels, 1),
        "per_class": per_class,
        "n_pixels": float(n_pixels),
    }


def save_checkpoint(
    path: Path,
    model: nn.Module,
    ema: EMA,
    optimizer: torch.optim.Optimizer,
    config: TrainingConfig,
    epoch: int,
    best_val_fg_miou: float,
    val: dict[str, Any],
    class_weights: dict[int, float],
) -> None:
    """Save the artefact using the EMA weights (engine-compatible contract)."""
    ema.apply_shadow(model)
    ema_state = model.state_dict()
    ema.restore(model)
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "model_state": ema_state,
            "model_arch": config.model_arch,
            "base": config.base,
            "epoch": epoch,
            "best_val_fg_miou": best_val_fg_miou,
            "val": val,
            "ema_state": ema.state_dict(),
            "optimizer_state": optimizer.state_dict(),
            "config": asdict(config),
            "class_weights": class_weights,
            "git_revision": git_revision(),
        },
        path,
    )


def append_registry(registry_path: Path, entry: dict[str, Any]) -> None:
    """Append one run entry to the experiment registry (git-ignored)."""
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    data = json.loads(registry_path.read_text(encoding="utf-8")) if registry_path.exists() else []
    data = [*data, entry]
    registry_path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def parse_args() -> TrainingConfig:
    parser = argparse.ArgumentParser(description="Baseline-vs-hybrid segmentation training.")
    parser.add_argument("--data-root", required=True, type=Path)
    parser.add_argument(
        "--label",
        default="research",
        type=str,
        help="experiment directory under ml/experiments/<label>",
    )
    parser.add_argument(
        "--model",
        default="hybrid",
        choices=[
            "baseline",
            "resnet34_unet",
            "hybrid",
            "hybrid_segmentation",
            "cardd_unet",
            "cardd_hybrid",
        ],
    )
    parser.add_argument("--epochs", type=int, default=60)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--grad-accum", type=int, default=2)
    parser.add_argument("--base", type=int, default=0)
    parser.add_argument("--lr-backbone", type=float, default=1e-4)
    parser.add_argument("--lr-head", type=float, default=3e-4)
    parser.add_argument(
        "--lr",
        type=float,
        default=None,
        help="legacy alias: sets both LR groups to this value",
    )
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--warmup-epochs", type=int, default=5)
    parser.add_argument("--min-lr", type=float, default=1e-6)
    parser.add_argument("--patience", type=int, default=10)
    parser.add_argument("--ema-decay", type=float, default=0.999)
    parser.add_argument("--train-limit", type=int, default=None)
    parser.add_argument("--val-limit", type=int, default=None)
    parser.add_argument("--no-augment", action="store_true")
    parser.add_argument("--no-class-sampling", action="store_true")
    parser.add_argument("--no-pretrained", action="store_true")
    parser.add_argument("--pretrained-path", type=str, default=None)
    parser.add_argument("--no-freeze-encoder-bn", action="store_true")
    parser.add_argument("--checkpoint-every", type=int, default=5)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--num-workers", type=int, default=0)
    args = parser.parse_args()

    lr_backbone = args.lr_backbone
    lr_head = args.lr_head
    if args.lr is not None:
        lr_backbone = args.lr
        lr_head = args.lr

    return TrainingConfig(
        data_root=str(args.data_root),
        model_arch=args.model,
        epochs=args.epochs,
        batch_size=args.batch_size,
        grad_accum=args.grad_accum,
        base=args.base,
        lr_backbone=lr_backbone,
        lr_head=lr_head,
        weight_decay=args.weight_decay,
        warmup_epochs=args.warmup_epochs,
        min_lr=args.min_lr,
        patience=args.patience,
        ema_decay=args.ema_decay,
        train_limit=args.train_limit,
        val_limit=args.val_limit,
        augment_train=not args.no_augment,
        class_sampling=not args.no_class_sampling,
        pretrained=not args.no_pretrained,
        pretrained_path=args.pretrained_path,
        freeze_encoder_bn=not args.no_freeze_encoder_bn,
        checkpoint_every=args.checkpoint_every,
        seed=args.seed,
        num_workers=args.num_workers,
        experiment_label=args.label,
    )


def main() -> None:
    config = parse_args()
    seed_all(config.seed)
    data_root = Path(config.data_root)
    use_cuda = torch.cuda.is_available()
    device = torch.device("cuda" if use_cuda else "cpu")
    scaler: Any = torch.amp.GradScaler("cuda", enabled=True) if use_cuda else None  # type: ignore[attr-defined]

    probe = CarddInstanceSegDataset(data_root, split=config.split, limit=1, seed=config.seed)
    num_classes = max(probe.category_ids()) + 1  # background + 6 CarDD classes
    model: nn.Module = build_model(
        config.model_arch,
        num_classes,
        config.base,
        config.pretrained,
        config.pretrained_path,
    ).to(device)

    stats = get_train_class_stats(data_root, config.split)
    weights = ClassWeights(foreground=stats.foreground_weights, background=stats.background_weight)
    sampler_weights: list[float] | None
    if config.class_sampling and config.train_limit is None:
        sampler_weights = stats.sampling_weights
        print("class-aware sampling: enabled (train split statistic)")
    else:
        sampler_weights = None
        print("class-aware sampling: disabled (limited run or flag)")

    optimizer = build_optimizer(model, config)
    scheduler = WarmupCosineLR(
        optimizer,
        warmup_epochs=config.warmup_epochs,
        total_epochs=config.epochs,
        min_lr=config.min_lr,
    )
    ema = EMA(model, decay=config.ema_decay)
    train_loader = make_train_loader(data_root, config, sampler_weights)
    val_loader = make_val_loader(data_root, config)

    n_params = sum(p.numel() for p in model.parameters())
    print(
        f"device={device} model={config.model_arch} params={n_params} "
        f"train={len(cast(Sized, train_loader.dataset))} "
        f"val={len(cast(Sized, val_loader.dataset))} "
        f"effective_batch={config.batch_size * config.grad_accum}"
    )
    print(
        f"foreground weights={ {cid: round(v, 3) for cid, v in stats.foreground_weights.items()} }"
    )

    out_dir = _REPO_ROOT / "ml" / "experiments" / config.experiment_label
    out_dir.mkdir(parents=True, exist_ok=True)

    epochs_detail: list[dict[str, Any]] = []
    best_miou = -1.0
    best_epoch = -1
    epochs_since_improvement = 0
    early_stopped_at: int | None = None
    if use_cuda:
        torch.cuda.reset_peak_memory_stats()

    for epoch in range(config.epochs):
        scheduler.step(epoch)
        epoch_start = time.perf_counter()

        tr = train_epoch(
            train_loader,
            model,
            optimizer,
            scaler,
            ema,
            device,
            num_classes,
            weights,
            config,
        )

        ema.apply_shadow(model)
        val = evaluate(val_loader, model, device, num_classes)
        ema.restore(model)

        elapsed = time.perf_counter() - epoch_start
        lr_now = scheduler.get_last_lr()
        improved = float(val["foreground_miou"]) > best_miou + 1e-6
        if improved:
            best_miou = float(val["foreground_miou"])
            best_epoch = epoch
            epochs_since_improvement = 0
            save_checkpoint(
                out_dir / "best_checkpoint.pt",
                model,
                ema,
                optimizer,
                config,
                epoch,
                best_miou,
                val,
                stats.foreground_weights,
            )
        else:
            epochs_since_improvement += 1

        if config.checkpoint_every > 0 and (epoch + 1) % config.checkpoint_every == 0:
            save_checkpoint(
                out_dir / f"periodic_epoch_{epoch:04d}.pt",
                model,
                ema,
                optimizer,
                config,
                epoch,
                best_miou,
                val,
                stats.foreground_weights,
            )

        epochs_detail.append(
            {
                "epoch": epoch,
                "lr": [round(v, 8) for v in lr_now],
                "train": tr,
                "val": val,
                "elapsed_secs": round(elapsed, 2),
                "ema": bool(improved and best_epoch == epoch),
            }
        )
        print(
            f"epoch {epoch:02d} lr={lr_now[0]:.2e}/{lr_now[-1]:.2e} "
            f"train_loss={tr['total_loss']:.4f} val_fgIoU={val['foreground_miou']:.4f} "
            f"val_fgDice={val['foreground_mdice']:.4f} acc={val['pixel_accuracy']:.4f} "
            f"[{elapsed:.1f}s]"
        )

        if epochs_since_improvement >= config.patience:
            early_stopped_at = epoch
            print(f"early stopping: no fg-mIoU improvement for {config.patience} epochs")
            break

    peak_vram_mb = float(torch.cuda.max_memory_allocated()) / 1e6 if use_cuda else 0.0
    record: dict[str, Any] = {
        "experiment_id": f"{config.experiment_label}-{datetime.now(UTC):%Y%m%d-%H%M%S}",
        "config": asdict(config),
        "dataset": "CarDD-COCO official splits",
        "model": (f"{config.model_arch} num_classes={num_classes} params={n_params}"),
        "device": str(device),
        "git_revision": git_revision(),
        "class_weights": stats.foreground_weights,
        "background_weight": stats.background_weight,
        "class_sampling": sampler_weights is not None,
        "effective_batch_size": config.batch_size * config.grad_accum,
        "peak_vram_mb": peak_vram_mb,
        "epochs_detail": epochs_detail,
        "best_val_foreground_miou": best_miou,
        "best_epoch": best_epoch,
        "early_stopped_at": early_stopped_at,
        "ema_decay": config.ema_decay,
        "note": "foreground metrics exclude background; checkpoint holds EMA weights",
    }
    (out_dir / "run_record.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    append_registry(
        out_dir.parent / "registry.json",
        {
            k: record[k]
            for k in ("experiment_id", "config", "best_val_foreground_miou", "git_revision")
        },
    )
    print(f"run record written to {out_dir / 'run_record.json'}")
    print(f"best val foreground mIoU={best_miou:.4f} (epoch {best_epoch})")


if __name__ == "__main__":
    main()
