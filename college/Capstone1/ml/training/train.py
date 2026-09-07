"""Phase 4+ real training instrumented with mIoU/Dice and a checkpoint registry.

Builds on the Phase 3 smoke run: same adapter → dataloader → CarddUNet →
cross-entropy stack (ADR 0008), plus per-epoch validation with per-class
IoU/Dice, an optional train-side augmentation, an LR schedule, and a run
registry appended under `ml/experiments/registry.json` (git-ignored; only
experiment IDs enter committed docs).

This is the experiment harness, not the final research pipeline: the metric
set and architecture remain provisional until the research document arrives.

Example (train subset, `ai` env):

    python ml/training/train.py \\
        --data-root datasets/CarDD_COCO \\
        --out-dir ml/experiments/phase4_baseline \\
        --epochs 5 --train-limit 192 --val-limit 64 --batch-size 2
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

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
from ml.models.cardd_unet import CarddUNet  # noqa: E402
from ml.training.cardd_dataset import CarddInstanceSegDataset, collate_seg  # noqa: E402
from ml.training.loss import aggregate_targets, cross_entropy_loss  # noqa: E402


@dataclass
class TrainingConfig:
    """Reproducible experiment settings (recorded verbatim per run)."""

    data_root: str
    split: str = "train2017"
    epochs: int = 5
    batch_size: int = 2
    base: int = 32
    lr: float = 1e-3
    weight_decay: float = 1e-5
    train_limit: int | None = None
    val_limit: int | None = None
    augment_train: bool = True
    seed: int = 0
    experiment_label: str = "phase4_baseline"


def git_revision() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True)
            .strip()
            .splitlines()[0]
        )
    except subprocess.CalledProcessError:
        return "unknown"


def make_loader(
    data_root: Path,
    split: str,
    config: TrainingConfig,
    augment: bool,
) -> torch.utils.data.DataLoader[Any]:
    limit = config.train_limit if split == "train2017" else config.val_limit
    ds = CarddInstanceSegDataset(
        data_root, split=split, limit=limit, seed=config.seed, augment=augment
    )
    return torch.utils.data.DataLoader(
        ds,
        batch_size=config.batch_size,
        shuffle=(split == "train2017"),
        num_workers=0,
        drop_last=False,
        collate_fn=collate_seg,
    )


def train_epoch(
    loader: torch.utils.data.DataLoader[Any],
    model: nn.Module,
    optimizer: torch.optim.Optimizer,
    device: torch.device,
    num_classes: int,
) -> dict[str, float]:
    model.train()
    total_ce, n_batches = 0.0, 0
    for batch in loader:
        images = batch["image"].to(device)
        masks = batch["masks"].to(device)
        labels = batch["labels"].to(device)
        logits = model(images)
        loss = cross_entropy_loss(logits, masks, labels, num_classes=num_classes)
        loss.backward()  # type: ignore[no-untyped-call]
        optimizer.step()
        optimizer.zero_grad()
        total_ce += float(loss.item())
        n_batches += 1
    return {"mean_ce": total_ce / max(n_batches, 1), "n_batches": float(n_batches)}


@torch.no_grad()
def evaluate(
    loader: torch.utils.data.DataLoader[Any],
    model: nn.Module,
    device: torch.device,
    num_classes: int,
) -> dict[str, Any]:
    """Full-dataset validation: per-class + macro IoU/Dice, pixel accuracy."""
    model.eval()
    conf = torch.zeros(num_classes, num_classes, dtype=torch.long, device=device)
    total_ce, n_batches = 0.0, 0
    correct, n_pixels = 0, 0
    for batch in loader:
        images = batch["image"].to(device)
        masks = batch["masks"].to(device)
        labels = batch["labels"].to(device)
        targets = aggregate_targets(masks, labels, num_classes)
        logits = model(images)
        total_ce += float(cross_entropy_loss(logits, masks, labels, num_classes=num_classes))
        n_batches += 1

        pred_classes = logits.argmax(dim=1)
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
        "mean_ce": total_ce / max(n_batches, 1),
        "n_batches": float(n_batches),
        "mean_iou": mean_iou(conf),
        "mean_dice": mean_dice(conf),
        "per_class": per_class,
        "pixel_accuracy": correct / max(n_pixels, 1),
        "n_pixels": float(n_pixels),
    }


def parse_args() -> TrainingConfig:
    parser = argparse.ArgumentParser(description="Phase 4 segmentation training run.")
    parser.add_argument("--data-root", required=True, type=Path)
    parser.add_argument("--label", default="phase4_baseline", type=str)
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--base", type=int, default=32)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--weight-decay", type=float, default=1e-5)
    parser.add_argument("--train-limit", type=int, default=None)
    parser.add_argument("--val-limit", type=int, default=None)
    parser.add_argument("--no-augment", action="store_true")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    return TrainingConfig(
        data_root=str(args.data_root),
        epochs=args.epochs,
        batch_size=args.batch_size,
        base=args.base,
        lr=args.lr,
        weight_decay=args.weight_decay,
        train_limit=args.train_limit,
        val_limit=args.val_limit,
        augment_train=not args.no_augment,
        seed=args.seed,
        experiment_label=args.label,
    )


def append_registry(registry_path: Path, entry: dict[str, Any]) -> None:
    """Append one run entry to the experiment registry (git-ignored)."""
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    data = json.loads(registry_path.read_text(encoding="utf-8")) if registry_path.exists() else []
    data = [*data, entry]
    registry_path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def seed_all(seed: int) -> None:
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def main() -> None:
    config = parse_args()
    seed_all(config.seed)
    data_root = Path(config.data_root)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    probe = CarddInstanceSegDataset(data_root, split=config.split, limit=1, seed=config.seed)
    num_classes = max(probe.category_ids()) + 1  # background + 6 CarDD classes
    model = CarddUNet(num_classes=num_classes, base=config.base).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=config.lr, weight_decay=config.weight_decay)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=config.epochs)

    train_loader = make_loader(data_root, "train2017", config, augment=config.augment_train)
    val_loader = make_loader(data_root, "val2017", config, augment=False)

    print(f"device={device}  model_params={sum(p.numel() for p in model.parameters())}")
    epochs_detail: list[dict[str, Any]] = []
    best_miou = -1.0
    for e in range(config.epochs):
        tr = train_epoch(
            train_loader,
            model,
            optimizer,
            device,
            num_classes=num_classes,
        )
        val = evaluate(
            val_loader,
            model,
            device,
            num_classes=num_classes,
        )
        lr_now = float(scheduler.get_last_lr()[0])
        epochs_detail.append({"epoch": e, "lr": lr_now, "train": tr, "val": val})
        print(
            f"epoch {e}: train={tr['mean_ce']:.4f}  val_mIoU={val['mean_iou']:.4f} "
            f"val_mDice={val['mean_dice']:.4f}  val_acc={val['pixel_accuracy']:.4f}"
        )
        scheduler.step()
        if val["mean_iou"] > best_miou:
            best_miou = float(val["mean_iou"])
            chk = _REPO_ROOT / "ml" / "experiments" / config.experiment_label
            chk.mkdir(parents=True, exist_ok=True)
            torch.save(
                {"model_state": model.state_dict(), "base": config.base, "epoch": e},
                chk / "best_checkpoint.pt",
            )

    record: dict[str, Any] = {
        "experiment_id": (f"{config.experiment_label}-{datetime.now(UTC):%Y%m%d-%H%M%S}"),
        "config": asdict(config),
        "dataset": "CarDD-COCO official splits",
        "model": f"CarddUNet base={config.base} num_classes={num_classes}",
        "device": str(device),
        "git_revision": git_revision(),
        "epochs_detail": epochs_detail,
        "best_val_mean_iou": best_miou,
        "note": "subset sizes per config; not the final research run",
    }
    out_dir = _REPO_ROOT / "ml" / "experiments" / config.experiment_label
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "run_record.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    append_registry(
        out_dir.parent / "registry.json",
        {k: record[k] for k in ("experiment_id", "config", "best_val_mean_iou", "git_revision")},
    )
    print(f"run record written to {out_dir / 'run_record.json'}")


if __name__ == "__main__":
    main()
