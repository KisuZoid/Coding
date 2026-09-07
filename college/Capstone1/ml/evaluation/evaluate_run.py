"""Phase 7 evaluation harness: full-split metrics + qualitative outputs.

Loads a trained checkpoint (produced by `ml/training/train.py`) and computes,
for the validation and test splits, the full metric set locked in
`docs/research/segmentation-experiment-config.md`:

  - overall: mean IoU, mean Dice, mean precision, mean recall, pixel accuracy;
  - per-class: IoU, Dice, precision, recall (channels 1..6);
  - small-damage slice: the same means restricted to small instances using the
    criterion in `ml/evaluation/small_damage.py`.

Writes `evaluation_summary.json` and, for a strided sample of images, a
qualitative montage (original / GT / prediction / overlay) into
`<out_dir>/evaluation/`. Artifacts live outside git under `ml/experiments/`.

Example (`ai` env):

    python ml/evaluation/evaluate_run.py \\
        --data-root datasets/CarDD_COCO \\
        --run-dir ml/experiments/phase4_baseline \\
        --num-examples 8
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import cv2
import numpy as np
import torch

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from ml.datasets.cardd_adapter import CarddAdapter  # noqa: E402
from ml.evaluation.metrics import (  # noqa: E402
    confusion_matrix,
    mean_dice,
    mean_iou,
    mean_precision,
    mean_recall,
    per_class_dice,
    per_class_iou,
    per_class_precision,
    per_class_recall,
)
from ml.evaluation.small_damage import (  # noqa: E402
    SmallDamageSlice,
    quantile_area,
    small_damage_summary,
)
from ml.models.cardd_unet import CarddUNet  # noqa: E402
from ml.training.cardd_dataset import (  # noqa: E402
    TARGET_SIZE,
    CarddInstanceSegDataset,
    collate_seg,
)
from ml.training.loss import aggregate_targets  # noqa: E402

CLASS_COLORS = {
    0: (0, 0, 0),  # background
    1: (0, 200, 255),  # dent
    2: (0, 128, 255),  # scratch
    3: (255, 0, 0),  # crack
    4: (255, 255, 0),  # glass shatter
    5: (180, 105, 255),  # lamp broken
    6: (0, 255, 0),  # tire flat
}


def git_revision() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True)
            .strip()
            .splitlines()[0]
        )
    except subprocess.CalledProcessError:
        return "unknown"


def instance_areas_by_image_id(data_root: Path, split: str) -> dict[int, list[float]]:
    """Map image_id -> per-instance mask area at 512x512 (instance order)."""
    adapter = CarddAdapter(data_root, split)
    result: dict[int, list[float]] = {}
    target = (TARGET_SIZE, TARGET_SIZE)
    for img in adapter.images():
        masks = adapter.rasterize(img)
        result[img.image_id] = [
            float(cv2.resize(m, target, interpolation=cv2.INTER_NEAREST).sum()) for m in masks
        ]
    return result


@torch.no_grad()
def evaluate_split(
    loader: torch.utils.data.DataLoader[Any],
    model: torch.nn.Module,
    device: torch.device,
    num_classes: int,
    small_slice: SmallDamageSlice,
    areas_by_id: dict[int, list[float]],
) -> dict[str, Any]:
    """Full metrics + small-damage slice over one split."""
    model.eval()
    conf = torch.zeros(num_classes, num_classes, dtype=torch.long, device=device)
    small_conf = torch.zeros(num_classes, num_classes, dtype=torch.long, device=device)
    correct, n_pixels = 0, 0

    for batch in loader:
        images = batch["image"].to(device)
        masks = batch["masks"]
        labels = batch["labels"]
        targets = aggregate_targets(masks, labels, num_classes).to(device)
        logits = model(images).float()
        pred_classes = logits.argmax(dim=1)
        target_classes = targets.argmax(dim=1)

        conf += confusion_matrix(pred_classes, target_classes, num_classes).to(device).long()
        match = pred_classes == target_classes
        correct += int(match.sum())
        n_pixels += int(torch.numel(target_classes))

        for i, img_id in enumerate(batch["image_id"].tolist()):
            areas = areas_by_id.get(int(img_id), [])
            small_target = small_slice.target_classes(
                small_slice.small_mask(masks[i].numpy(), areas[: masks[i].shape[0]]),
                labels[i][: masks[i].shape[0]].numpy(),
            ).to(device)
            small_conf += (
                confusion_matrix(pred_classes[i], small_target, num_classes).to(device).long()
            )

    conf = conf.cpu()
    small_conf = small_conf.cpu()
    per_class: dict[str, dict[str, float]] = {}
    for c, (i, d, p, r) in enumerate(
        zip(
            per_class_iou(conf),
            per_class_dice(conf),
            per_class_precision(conf),
            per_class_recall(conf),
            strict=True,
        )
    ):
        per_class[str(c)] = {
            "iou": float(i),
            "dice": float(d),
            "precision": float(p),
            "recall": float(r),
        }

    summary = {
        "mean_iou": mean_iou(conf),
        "mean_dice": mean_dice(conf),
        "mean_precision": mean_precision(conf),
        "mean_recall": mean_recall(conf),
        "pixel_accuracy": correct / max(n_pixels, 1),
        "per_class": per_class,
        "n_pixels": float(n_pixels),
    }
    summary.update(small_damage_summary(small_conf))
    return summary


def examples_wanted(num_examples: int, written: int) -> bool:
    return written < num_examples


@torch.no_grad()
def write_examples(
    loader: torch.utils.data.DataLoader[Any],
    model: torch.nn.Module,
    device: torch.device,
    num_classes: int,
    num_examples: int,
    examples_dir: Path,
    label: str,
) -> list[dict[str, Any]]:
    """Write montage images (original / GT / prediction / overlay) for a sample."""
    examples_dir.mkdir(parents=True, exist_ok=True)
    model.eval()
    written = 0
    for batch in loader:
        images = batch["image"].to(device)
        masks = batch["masks"]
        labels = batch["labels"]
        targets = aggregate_targets(masks, labels, num_classes).to(device)
        logits = model(images).float()
        pred_classes = logits.argmax(dim=1).cpu()
        for i in range(images.shape[0]):
            if written >= num_examples:
                return []
            img_id = int(batch["image_id"][i])
            image_np = (images[i].cpu().permute(1, 2, 0).numpy() * 255).astype(np.uint8)
            gt = overlay_class_mask(image_np, targets[i].argmax(dim=0).cpu().numpy())
            pred = overlay_class_mask(image_np, pred_classes[i].numpy())
            both = overlay_class_mask(
                image_np,
                targets[i].argmax(dim=0).cpu().numpy(),
                pred_classes[i].numpy(),
            )
            montage = np.concatenate([np.hstack([image_np, gt]), np.hstack([pred, both])], axis=0)
            out = examples_dir / f"{label}_{img_id:06d}_{written:02d}.png"
            cv2.imwrite(str(out), cv2.cvtColor(montage, cv2.COLOR_RGB2BGR))
            written += 1
    return []


def overlay_class_mask(
    image: np.ndarray,
    gt: np.ndarray,
    pred: np.ndarray | None = None,
) -> np.ndarray:
    """Return a copy of `image` with class masks color-coded as an overlay.

    When `pred` is provided, ground truth is drawn as solid fill and prediction
    as colored edges, giving a single comparison overlay.
    """
    overlay = image.copy()
    if pred is None:
        for class_id, color in CLASS_COLORS.items():
            if class_id == 0:
                continue
            overlay[gt == class_id] = blend(overlay[gt == class_id], color, 0.6)
        return overlay
    for class_id, color in CLASS_COLORS.items():
        if class_id == 0:
            continue
        mask_gt = gt == class_id
        overlay[mask_gt] = blend(overlay[mask_gt], color, 0.55)
        edges = edge_of(pred == class_id)
        overlay[edges] = color
    return overlay


def blend(pixels: np.ndarray, color: tuple[int, int, int], alpha: float) -> np.ndarray:
    """Pixels (N,3) uint8 -> alpha-blend toward `color`."""
    blended = pixels.astype(np.float32) * (1.0 - alpha)
    blended += np.asarray(color, dtype=np.float32) * alpha
    return blended.astype(np.uint8)


def edge_of(mask: np.ndarray) -> np.ndarray:
    """Draw the boundary of a binary mask (dilate minus own pixels)."""
    kernel = np.ones((5, 5), np.uint8)
    return (cv2.dilate(mask.astype(np.uint8), kernel) - mask.astype(np.uint8)) > 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Phase 7 evaluation harness.")
    parser.add_argument("--data-root", required=True, type=Path)
    parser.add_argument("--run-dir", required=True, type=Path, help="ml/experiments/<label>")
    parser.add_argument("--base", type=int, default=None, help="override base from checkpoint")
    parser.add_argument("--num-examples", type=int, default=8)
    parser.add_argument("--limit", type=int, default=None, help="limit images per split (dev)")
    parser.add_argument("--batch-size", type=int, default=2)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_dir = _REPO_ROOT / "ml" / "experiments" / args.run_dir.name
    if not run_dir.exists() and not args.run_dir.is_absolute():
        raise SystemExit(f"run dir not found: {args.run_dir}")
    run_dir = args.run_dir if args.run_dir.is_absolute() else run_dir
    ckpt_path = run_dir / "best_checkpoint.pt"
    if not ckpt_path.exists():
        raise SystemExit(f"missing checkpoint: {ckpt_path}")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    ckpt = torch.load(ckpt_path, map_location=device, weights_only=False)
    base = args.base if args.base is not None else int(ckpt.get("base", 32))

    probe = CarddInstanceSegDataset(args.data_root, "val2017", limit=1)
    num_classes = max(probe.category_ids()) + 1
    model = CarddUNet(num_classes=num_classes, base=base).to(device)
    model.load_state_dict(ckpt["model_state"])

    threshold = quantile_area(0.25, str(args.data_root))  # train-split p25
    slice_ = SmallDamageSlice(threshold)

    results: dict[str, Any] = {
        "git_revision": git_revision(),
        "checkpoint": str(ckpt_path),
        "small_damage_threshold_px512": threshold,
        "device": str(device),
    }
    examples_dir = run_dir / "evaluation"
    for split in ("val2017", "test2017"):
        ds = CarddInstanceSegDataset(args.data_root, split, limit=args.limit)
        loader = torch.utils.data.DataLoader(
            ds, batch_size=args.batch_size, shuffle=False, num_workers=0, collate_fn=collate_seg
        )
        areas = instance_areas_by_image_id(args.data_root, split)
        summary = evaluate_split(loader, model, device, num_classes, slice_, areas)
        summary["n_images"] = float(len(ds))
        results[split] = summary
        write_examples(loader, model, device, num_classes, args.num_examples, examples_dir, split)

    out = run_dir / "evaluation_summary.json"
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"threshold p25px={threshold:.0f}")
    for split in ("val2017", "test2017"):
        r = results[split]
        print(
            f"{split}: mIoU={r['mean_iou']:.4f} mDice={r['mean_dice']:.4f} "
            f"mPrec={r['mean_precision']:.4f} mRec={r['mean_recall']:.4f} "
            f"pxAcc={r['pixel_accuracy']:.4f} smallIoU={r['small_mean_iou']:.4f} "
            f"smallRec={r['small_mean_recall']:.4f}"
        )
    print(f"summary -> {out}")


if __name__ == "__main__":
    main()
