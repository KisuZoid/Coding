"""CarDD-COCO dataset audit (Phase 1).

Produces a JSON report of dataset statistics used to decide training choices:
image/annotation counts per split, per-class statistics, mask areas, class
imbalance, multiple-damage images, annotation validity, and exact/near-duplicate
detection.

Run inside the `ai` conda environment:

    conda activate ai
    python ml/datasets/cardd_audit.py \\
        --data-root datasets/CarDD_COCO \\
        --out ml/datasets/reports/cardd_audit.json
"""

from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, cast

import cv2
import numpy as np

SPLITS = ["train2017", "val2017", "test2017"]
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp"}


def load_annotations(path: Path) -> dict[str, Any]:
    """Load a COCO JSON annotation file."""
    with path.open("r", encoding="utf-8") as fh:
        return cast(dict[str, Any], json.load(fh))


def rasterize_polygon(polygon: list[float], width: int, height: int) -> np.ndarray:
    """Rasterize a flat [x,y,...] polygon into a boolean mask."""
    mask = np.zeros((height, width), dtype=np.uint8)
    if len(polygon) < 6:
        return mask
    pts = np.array(polygon, dtype=np.float32).reshape(-1, 2).astype(np.int32)
    cv2.fillPoly(mask, [pts], 1)
    return mask.astype(bool)


def polygon_area(polygon: list[float]) -> float:
    """Shoelace area of a flat [x,y,...] polygon."""
    if len(polygon) < 6:
        return 0.0
    pts = np.array(polygon, dtype=np.float64).reshape(-1, 2)
    x, y = pts[:, 0], pts[:, 1]
    return float(0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))))


def raster_hash(img: np.ndarray, size: int = 12) -> str:
    """Perceptual-ish average hash: downscale to grayscale, threshold on mean."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (size, size), interpolation=cv2.INTER_AREA)
    mean = resized.mean()
    bits = (resized > mean).flatten().astype(np.uint8)
    return "".join(str(int(b)) for b in bits)


def condense_ratio(values: list[float]) -> dict[str, float | int]:
    """Condense a list of numbers into descriptive statistics."""
    if not values:
        return {"n": 0}
    return {
        "n": len(values),
        "mean": round(statistics.mean(values), 3),
        "median": round(statistics.median(values), 3),
        "std": round(statistics.pstdev(values), 3) if len(values) > 1 else 0.0,
        "min": round(min(values), 3),
        "max": round(max(values), 3),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit the CarDD-COCO dataset.")
    parser.add_argument("--data-root", required=True, type=Path, help="CarDD_COCO dataset dir")
    parser.add_argument("--out", required=True, type=Path, help="JSON report output path")
    parser.add_argument("--no-images", action="store_true", help="Skip reading image files")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root: Path = args.data_root
    annotations_dir = root / "annotations"

    by_split: dict[str, dict[str, Any]] = {}
    category_names: dict[int, str] = {}
    image_hashes: dict[str, list[str]] = defaultdict(list)

    for split in SPLITS:
        ann_file = annotations_dir / f"instances_{split}.json"
        if not ann_file.exists():
            by_split[split] = {"error": f"missing {ann_file.name}"}
            continue

        data = load_annotations(ann_file)
        categories = data.get("categories", [])
        for cat in categories:
            category_names[int(cat["id"])] = cat["name"]

        images = data.get("images", [])
        anns = data.get("annotations", [])

        ann_image_ids: Counter[int] = Counter()
        per_class_count: Counter[int] = Counter()
        per_class_ann_image: Counter[int] = Counter()
        per_class_area: defaultdict[int, list[float]] = defaultdict(list)
        masks_per_image: Counter[int] = Counter()
        ann_pixels: list[float] = []

        invalid_anns: dict[str, int] = {
            "empty_polygon": 0,
            "area_mismatch": 0,
            "bbox_out_of_bounds": 0,
            "annotation_id_missing": 0,
        }
        dimension_counter: Counter[tuple[int, int]] = Counter()
        aspect_ratios: list[float] = []

        missing_image_files = 0
        dup_groups: list[list[str]] = []

        for ann in anns:
            ann_image_ids[int(ann["image_id"])] += 1
            per_class_count[int(ann["category_id"])] += 1
            masks_per_image[int(ann["image_id"])] += 1

            category_id = int(ann["category_id"])
            per_class_ann_image[category_id] += 1

            if "id" not in ann:
                invalid_anns["annotation_id_missing"] += 1

            seg = ann.get("segmentation", [])
            img_matches = [i for i in images if int(i["id"]) == int(ann["image_id"])]
            width = int(img_matches[0]["width"]) if img_matches else 0
            height = int(img_matches[0]["height"]) if img_matches else 0

            if isinstance(seg, list) and seg and len(seg[0]) >= 6:
                poly = seg[0]
                shoelace = polygon_area(poly)
                expected = float(ann.get("area", 0))
                if abs(shoelace - expected) / max(expected, 1e-6) > 0.02:
                    invalid_anns["area_mismatch"] += 1

                if not args.no_images:
                    mask = rasterize_polygon(poly, width, height)
                    pixel_area = int(mask.sum())
                    ann_pixels.append(pixel_area)
                    per_class_area[category_id].append(pixel_area)

                bbox = [float(v) for v in ann.get("bbox", [0, 0, 0, 0])]
                if (bbox[0] + bbox[2]) > width + 1 or (bbox[1] + bbox[3]) > height + 1:
                    invalid_anns["bbox_out_of_bounds"] += 1
            else:
                invalid_anns["empty_polygon"] += 1

        for img in images:
            img_id = int(img["id"])
            w, h = int(img["width"]), int(img["height"])
            dimension_counter[(w, h)] += 1
            aspect_ratios.append(round(w / h, 4) if h else 0.0)
            if img_id not in ann_image_ids:
                masks_per_image[img_id] = 0

        if not args.no_images:
            for img in images:
                fname = root / split / img["file_name"]
                if not fname.exists():
                    missing_image_files += 1
                    continue
                arr = cv2.imread(str(fname))
                if arr is None:
                    missing_image_files += 1
                    continue
                img_hash = raster_hash(arr)
                image_hashes[f"{split}/{img['file_name']}"].append(img_hash)
            hash_to_files: dict[str, list[str]] = defaultdict(list)
            for fname, hashes in image_hashes.items():
                for h_val in hashes:
                    hash_to_files[h_val].append(fname)
            dup_groups = [sorted(files) for files in hash_to_files.values() if len(files) > 1]

        per_class: dict[str, dict[str, Any]] = {}
        for cat_id, name in category_names.items():
            areas = per_class_area.get(cat_id, [])
            per_class[name] = {
                "category_id": cat_id,
                "instance_count": per_class_count[cat_id],
                "images_with_class": per_class_ann_image[cat_id],
                "pixel_area": condense_ratio(areas) if areas else {"n": 0},
            }

        num_multi = sum(1 for c in masks_per_image.values() if c >= 2)
        ann_ids_in_images = set(int(i["id"]) for i in images)
        n_anns_missing_image = sum(
            c for img_id, c in ann_image_ids.items() if img_id not in ann_ids_in_images
        )

        by_split[split] = {
            "n_images": len(images),
            "n_annotations": len(anns),
            "n_images_with_annotations": len(ann_image_ids),
            "n_images_without_annotations": len(images) - len(ann_image_ids),
            "n_annotations_with_missing_image": n_anns_missing_image,
            "annotations_per_image": condense_ratio(list(masks_per_image.values())),
            "multi_damage_images": num_multi,
            "n_annotations_per_class": {
                category_names.get(k, k): v for k, v in per_class_count.items()
            },
            "per_class": per_class,
            "mask_pixels": condense_ratio(ann_pixels) if ann_pixels else {"n": 0},
            "image_dimensions": {
                f"{w}x{h}": c
                for (w, h), c in sorted(dimension_counter.items(), key=lambda kv: -kv[1])
            },
            "aspect_ratio": condense_ratio(aspect_ratios),
            "invalid_annotations": invalid_anns,
            "missing_image_files": missing_image_files,
            "duplicate_groups": dup_groups[:10],
            "n_duplicate_groups": len(dup_groups),
            "n_images_in_duplicate_groups": sum(len(g) for g in dup_groups),
        }

    train_counts = [
        by_split["train2017"]["per_class"][name]["instance_count"]
        for name in category_names.values()
    ]
    max_count = max(train_counts) if train_counts else 1

    report = {
        "dataset": "CarDD_COCO",
        "splits": by_split,
        "categories": category_names,
        "class_imbalance_ratio": {
            name: round(by_split["train2017"]["per_class"][name]["instance_count"] / max_count, 3)
            for name in category_names.values()
        },
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"Report written to {args.out}")
    print(f"Categories: {report['categories']}")
    for split, s in by_split.items():
        if "error" in s:
            print(f"  {split}: {s['error']}")
            continue
        print(
            f"  {split}: images={s['n_images']} anns={s['n_annotations']} "
            f"multi-damage={s['multi_damage_images']} "
            f"avg_anns/img={s['annotations_per_image']['mean']}"
        )
        for name, stats in s["per_class"].items():
            mean_area = stats["pixel_area"].get("mean", "N/A")
            print(f"      {name}: {stats['instance_count']} instances, area {mean_area}")


if __name__ == "__main__":
    main()
