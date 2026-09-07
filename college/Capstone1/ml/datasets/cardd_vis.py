"""Generate CarDD-COCO audit visualizations (Phase 1).

For a few sample images per damage class, writes a side-by-side panel of the
original image, the ground-truth mask, and the mask overlaid on the image, so
annotation quality can be checked by eye.

Run inside the `ai` conda environment:

    conda activate ai
    python ml/datasets/cardd_vis.py \\
        --data-root datasets/CarDD_COCO \\
        --out ml/datasets/reports/vis_samples
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import cv2
import numpy as np

from ml.datasets.cardd_audit import load_annotations, rasterize_polygon

CLASS_COLORS = {
    1: (255, 80, 80),  # dent
    2: (255, 200, 60),  # scratch
    3: (120, 255, 90),  # crack
    4: (80, 180, 255),  # glass shatter
    5: (220, 120, 255),  # lamp broken
    6: (255, 255, 255),  # tire flat
}


def draw_mask_overlay(img: np.ndarray, mask: np.ndarray, color: tuple[int, int, int]) -> np.ndarray:
    """Return img with the mask filled translucently and outlined."""
    out = img.copy()
    out[mask] = (0.45 * out[mask].astype(np.float32) + 0.55 * np.array(color)).astype(np.uint8)
    contours, _ = cv2.findContours(
        mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    cv2.drawContours(out, contours, -1, color, 2)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Render CarDD-COCO audit visualizations.")
    parser.add_argument("--data-root", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--per-class", type=int, default=3, help="samples per class per split")
    args = parser.parse_args()

    data = load_annotations(args.data_root / "annotations" / "instances_val2017.json")
    images = data.get("images", [])
    anns = data.get("annotations", [])
    img_by_id = {int(i["id"]): i for i in images}
    anns_by_img: dict[int, list[Any]] = {}
    for ann in anns:
        anns_by_img.setdefault(int(ann["image_id"]), []).append(ann)

    wanted: dict[int, list[Any]] = {cid: [] for cid in CLASS_COLORS}
    for ann in anns:
        cid = int(ann["category_id"])
        if cid in wanted and len(wanted[cid]) < args.per_class:
            wanted[cid].append(ann)

    args.out.mkdir(parents=True, exist_ok=True)
    class_names = {
        1: "dent",
        2: "scratch",
        3: "crack",
        4: "glass shatter",
        5: "lamp broken",
        6: "tire flat",
    }

    for cid, sample_anns in wanted.items():
        for i, ann in enumerate(sample_anns):
            img_info = img_by_id[int(ann["image_id"])]
            img_path = args.data_root / "val2017" / img_info["file_name"]
            img = cv2.imread(str(img_path))
            if img is None:
                print(f"  missing image: {img_path}")
                continue
            mask = np.zeros((img.shape[0], img.shape[1]), dtype=bool)
            for poly in ann.get("segmentation", []):
                mask |= rasterize_polygon(poly, img.shape[1], img.shape[0])
            color = CLASS_COLORS[cid]
            overlay = draw_mask_overlay(img, mask, color)
            title = f"class {class_names[cid]} | img {img_info['file_name']} | px {int(mask.sum())}"
            panel = np.hstack((img, overlay))
            cv2.putText(panel, title, (12, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 6)
            cv2.putText(panel, title, (12, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            fname = args.out / f"class{cid}_sample{i}_{img_info['file_name']}"
            cv2.imwrite(str(fname), panel)
    print(f"Wrote visualizations to {args.out}")
    print("Labels:", ", ".join(f"{k}: {v}" for k, v in sorted(class_names.items())))


if __name__ == "__main__":
    main()
