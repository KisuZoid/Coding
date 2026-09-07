"""Phase 9 qualitative error analysis: pick representative failure cases.

Scans the val2017 split with the best checkpoint and selects images for the
categories requested in the plan, writing one montage per category:

  - correct: highest per-image mIoU with >= 1 foreground-class pixel
  - small:   image whose largest damage instance is below the small-damage
             threshold (p25 of train per-instance area)
  - large:   largest per-instance area
  - multi:   most distinct damage classes present in GT
  - confusing: predicted class distribution differs most from GT (proxy for
             class-confusion, e.g. most misclassified foreground pixels)
  - fp:       highest false-positive pixel count (predicted damage but GT
             background)
  - fn:       highest false-negative pixel count (GT damage but predicted
             background)

The montage layout is (original / GT / pred / GT+pred overlay) as a 2x2 grid.
Written under `ml/experiments/<run>/evaluation/error_analysis/`.

Example (`ai` env):

    python ml/analysis/error_analysis.py \\
        --data-root datasets/CarDD_COCO \\
        --run-dir ml/experiments/cardd_baseline_ce
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import cv2
import numpy as np
import torch

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from ml.evaluation.evaluate_run import CLASS_COLORS  # noqa: E402
from ml.evaluation.small_damage import quantile_area  # noqa: E402
from ml.models.cardd_unet import CarddUNet  # noqa: E402
from ml.training.cardd_dataset import CarddInstanceSegDataset, collate_seg  # noqa: E402
from ml.training.loss import aggregate_targets  # noqa: E402


def blend(pixels: np.ndarray, color: tuple[int, int, int], alpha: float) -> np.ndarray:
    blended = pixels.astype(np.float32) * (1.0 - alpha)
    blended += np.asarray(color, dtype=np.float32) * alpha
    return blended.astype(np.uint8)


def overlay(
    image: np.ndarray, gt: np.ndarray, pred: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    gt_img = image.copy()
    pred_img = image.copy()
    both = image.copy()
    for cid, color in CLASS_COLORS.items():
        if cid == 0:
            continue
        gm = gt == cid
        pm = pred == cid
        gt_img[gm] = blend(gt_img[gm], color, 0.6)
        pred_img[pm] = blend(pred_img[pm], color, 0.6)
        both[gm] = blend(both[gm], color, 0.55)
        for y, x_ in np.argwhere(pm):
            both[y, x_] = blend(both[y, x_], color, 0.35)
    return gt_img, pred_img, both


def montage(original: np.ndarray, gt: np.ndarray, pred: np.ndarray) -> np.ndarray:
    gt_img, pred_img, both = overlay(original, gt, pred)
    top = np.hstack([original, gt_img])
    bottom = np.hstack([pred_img, both])
    return np.vstack([top, bottom])


def label_bar(name: str) -> np.ndarray:
    bar = np.full((40, 1024, 3), 255, dtype=np.uint8)
    cv2.putText(bar, name, (8, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (30, 30, 30), 2, cv2.LINE_AA)
    return bar


def analyze_run(data_root: Path, run_dir: Path, base: int | None) -> dict[str, Any]:
    ckpt_path = run_dir / "best_checkpoint.pt"
    if not ckpt_path.exists():
        raise SystemExit(f"missing checkpoint: {ckpt_path}")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    ckpt = torch.load(ckpt_path, map_location=device, weights_only=False)
    b = base if base is not None else int(ckpt.get("base", 32))
    probe = CarddInstanceSegDataset(data_root, "val2017", limit=1)
    num_classes = max(probe.category_ids()) + 1
    model = CarddUNet(num_classes=num_classes, base=b).to(device)
    model.load_state_dict(ckpt["model_state"])
    model.eval()

    threshold = quantile_area(0.25, str(data_root))

    ds = CarddInstanceSegDataset(data_root, "val2017")
    loader = torch.utils.data.DataLoader(
        ds, batch_size=2, shuffle=False, num_workers=0, collate_fn=collate_seg
    )

    per_image: dict[int, dict[str, Any]] = {}
    with torch.no_grad():
        for batch in loader:
            images = batch["image"].to(device)
            pred = model(images).argmax(1).cpu()
            tgt = aggregate_targets(batch["masks"], batch["labels"], num_classes).cpu()
            tgt_classes = tgt.argmax(1)
            for i in range(images.shape[0]):
                img_id = int(batch["image_id"][i])
                p = pred[i]
                t = tgt_classes[i]
                pix = int(torch.numel(t))
                correct = int((p == t).sum())
                tp = int(((p == t) & (t > 0)).sum())
                fp = int(((p != t) & (p > 0)).sum())
                fn = int(((p != t) & (t > 0)).sum())
                per_image[img_id] = {
                    "m_iou": correct / max(pix, 1),
                    "gt_fg_px": int(tgt[:, 1:].sum().item()),
                    "pred_fg_px": int((p > 0).sum()),
                    "fg_correct": tp,
                    "fp": fp,
                    "fn": fn,
                    "image": images[i].cpu().permute(1, 2, 0).mul(255).byte().numpy().copy(),
                    "gt": t.numpy(),
                    "pred": p.numpy(),
                    "file": batch["file_name"][i],
                    "inst_areas": _instance_areas(batch["masks"][i], batch["labels"][i]),
                    "n_classes": int((torch.bincount(t.flatten(), minlength=num_classes) > 0).sum())
                    - int((t == 0).any()),
                }

    return _select(per_image, threshold)


def _instance_areas(masks: torch.Tensor, labels: torch.Tensor) -> list[float]:
    areas: list[float] = []
    for m, lab in zip(masks, labels, strict=True):
        if int(lab) < 0:
            continue
        areas.append(float(m.sum()))
    return areas


def _select(per_image: dict[int, dict[str, Any]], threshold: float) -> dict[str, dict[str, Any]]:
    images = list(per_image.values())
    with_gt = [im for im in images if im["gt_fg_px"] > 0]
    out: dict[str, dict[str, Any]] = {}

    correct = max(with_gt, key=lambda im: (im["fg_correct"], im["gt_fg_px"]))
    out["correct"] = correct

    small = min(
        with_gt,
        key=lambda im: max((a for a in im["inst_areas"] if a < threshold), default=float("inf")),
    )
    out["small"] = small

    large = max(with_gt, key=lambda im: max((a for a in im["inst_areas"]), default=0))
    out["large"] = large

    multi = max(with_gt, key=lambda im: im["n_classes"])
    out["multi"] = multi

    confusing = max(
        [im for im in with_gt if im["fp"] + im["fn"] > 0],
        key=lambda im: im["fp"] + im["fn"] - im["fg_correct"],
        default=correct,
    )
    out["confusing"] = confusing

    out["fp"] = max(with_gt, key=lambda im: im["fp"])
    out["fn"] = max(with_gt, key=lambda im: im["fn"])
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Phase 9 error analysis.")
    parser.add_argument("--data-root", required=True, type=Path)
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--base", type=int, default=None)
    args = parser.parse_args()

    run_dir: Path
    if args.run_dir.is_absolute():
        run_dir = args.run_dir
    else:
        run_dir = _REPO_ROOT / "ml" / "experiments" / args.run_dir.name
    selection = analyze_run(args.data_root, run_dir, args.base)
    out_dir = run_dir / "evaluation" / "error_analysis"
    out_dir.mkdir(parents=True, exist_ok=True)

    for name, im in selection.items():
        grid = montage(im["image"], im["gt"], im["pred"])
        data = {
            "category": name,
            "file": im["file"],
            "inst_areas_px512": im["inst_areas"],
            "gt_fg_px": im["gt_fg_px"],
            "pred_fg_px": im["pred_fg_px"],
            "fp_px": im["fp"],
            "fn_px": im["fn"],
            "n_classes": im["n_classes"],
        }
        (out_dir / "selection.json" if name == "correct" else None)
        cv2.imwrite(str(out_dir / f"{name}.png"), cv2.cvtColor(grid, cv2.COLOR_RGB2BGR))
        print(name, data)

    (out_dir / "selection.json").write_text(
        json.dumps(
            {
                key: {k: v for k, v in val.items() if k not in ("image", "gt", "pred")}
                for key, val in selection.items()
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"error analysis images -> {out_dir}")


if __name__ == "__main__":
    main()
