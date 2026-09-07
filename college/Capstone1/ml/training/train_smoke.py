"""Phase 3 tiny smoke training run (ADR 0006: raw PyTorch small U-Net).

Purpose: verify the machinery end-to-end on the RTX 3050 (~4 GB) — adapter →
dataloader → model → loss → backward → checkpoint → one inference pass — on a
tiny seeded sample. It makes no accuracy claim and runs a bounded number of
steps.

Assumes the `ai` conda environment:

    conda activate ai
    python ml/training/train_smoke.py \\
        --data-root datasets/CarDD_COCO \\
        --out-dir ml/experiments/phase3_smoke \\
        --epochs 2 --step-limit 20 --batch-size 2
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import torch
from torch import nn

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from ml.models.cardd_unet import CarddUNet  # noqa: E402
from ml.training.cardd_dataset import CarddInstanceSegDataset, collate_seg  # noqa: E402
from ml.training.loss import aggregate_targets, cross_entropy_loss  # noqa: E402

SEED = 0


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
    data_root: Path, split: str, limit: int, batch_size: int
) -> torch.utils.data.DataLoader[Any]:
    ds = CarddInstanceSegDataset(data_root, split=split, limit=limit, seed=SEED)
    return torch.utils.data.DataLoader(
        ds,
        batch_size=batch_size,
        shuffle=True,
        num_workers=0,
        drop_last=False,
        collate_fn=collate_seg,
    )


def run_one_epoch(
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


def infer_accuracy(
    loader: torch.utils.data.DataLoader[Any],
    model: nn.Module,
    device: torch.device,
    num_classes: int,
) -> dict[str, float]:
    model.eval()
    correct, total = 0, 0
    with torch.no_grad():
        for batch in loader:
            images = batch["image"].to(device)
            masks = batch["masks"].to(device)
            labels = batch["labels"].to(device)
            targets = aggregate_targets(masks, labels, num_classes).argmax(dim=1)
            logits = model(images)
            preds = logits.argmax(dim=1)
            match = preds == targets
            correct += int(match.sum())
            total += int(torch.numel(targets))
            break  # one batch is enough for the smoke sanity pass
    return {"pixel_accuracy": correct / max(total, 1), "n_pixels": float(total)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Phase 3 smoke training run.")
    parser.add_argument("--data-root", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--step-limit", type=int, default=24, help="samples per split")
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    base = 32  # smaller than the full U-Net default so the smoke loop is fast
    probe = CarddInstanceSegDataset(args.data_root, split="train2017", limit=1, seed=SEED)
    num_classes = max(probe.category_ids()) + 1  # background + 6 CarDD classes
    model = CarddUNet(num_classes=num_classes, base=base).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)

    train_loader = make_loader(args.data_root, "train2017", args.step_limit, args.batch_size)
    val_loader = make_loader(args.data_root, "val2017", args.step_limit, args.batch_size)

    print(f"device={device}  model_params={sum(p.numel() for p in model.parameters())}")
    epochs: list[dict[str, Any]] = []
    for e in range(args.epochs):
        tr = run_one_epoch(train_loader, model, optimizer, device, num_classes=num_classes)
        epochs.append({"epoch": e, **tr})
        print(f"epoch {e}: {tr}")

    val = infer_accuracy(val_loader, model, device, num_classes=num_classes)
    print(f"val: {val}")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    chk = args.out_dir / "checkpoint.pt"
    torch.save({"model_state": model.state_dict(), "base": base}, chk)

    record: dict[str, Any] = {
        "experiment_id": f"phase3-smoke-{datetime.now(UTC):%Y%m%d-%H%M%S}",
        "purpose": "smoke training run - machinery check only, no accuracy claim",
        "framework": "raw PyTorch (ADR 0006)",
        "model": f"CarddUNet base={base} num_classes={num_classes}",
        "dataset": "CarDD-COCO official splits",
        "samples_per_split": args.step_limit,
        "epochs": args.epochs,
        "epochs_detail": epochs,
        "val": val,
        "seed": args.seed,
        "device": str(device),
        "git_revision": git_revision(),
        "checkpoint": str(chk),
        "note": "random subset per split (seed); not a representative metric",
    }
    (args.out_dir / "run_record.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(f"run record written to {args.out_dir / 'run_record.json'}")


if __name__ == "__main__":
    main()
