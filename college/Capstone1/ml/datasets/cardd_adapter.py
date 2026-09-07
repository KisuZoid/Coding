"""CarDD-COCO data adapter (Phase 2).

Typed access to the CarDD-COCO dataset: category metadata, per-image
annotations, image loading, and polygon rasterization. Owns the COCO JSON layer
so that training, evaluation, and future pipelines never re-parse raw JSON and
never drift on split names, polygon layout, or category ids.

Run inside the `ai` conda environment (requires torch + opencv).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast

import cv2
import numpy as np

CARDD_SPLITS = ("train2017", "val2017", "test2017")


@dataclass(frozen=True)
class CarddCategory:
    id: int
    name: str


@dataclass(frozen=True)
class CarddAnnotation:
    category_id: int
    polygons: tuple[tuple[tuple[float, float], ...], ...]


@dataclass
class CarddImage:
    image_id: int
    file_name: str
    width: int
    height: int
    annotations: list[CarddAnnotation] = field(default_factory=list)


class CarddAdapter:
    """Read CarDD-COCO metadata, images, and masks through a validated API."""

    def __init__(self, data_root: Path | str, split: str) -> None:
        if split not in CARDD_SPLITS:
            raise ValueError(f"split must be one of {CARDD_SPLITS}, got {split!r}")
        self._root = Path(data_root)
        self._split = split
        self._categories, self._images = self._load()

    @staticmethod
    def _load_json(path: Path) -> dict[str, Any]:
        with path.open("r", encoding="utf-8") as fh:
            return cast(dict[str, Any], json.load(fh))

    @staticmethod
    def _to_polygons(seg: list[Any]) -> tuple[tuple[tuple[float, float], ...], ...]:
        polygons: list[tuple[tuple[float, float], ...]] = []
        for poly in seg:
            vals = [float(v) for v in poly]
            if len(vals) < 6:
                continue
            polygons.append(tuple(zip(vals[0::2], vals[1::2], strict=True)))
        return tuple(polygons)

    def _load(self) -> tuple[list[CarddCategory], list[CarddImage]]:
        ann_file = self._root / "annotations" / f"instances_{self._split}.json"
        if not ann_file.exists():
            raise FileNotFoundError(f"missing annotation file: {ann_file}")
        data = self._load_json(ann_file)

        categories = [
            CarddCategory(id=int(c["id"]), name=str(c["name"])) for c in data.get("categories", [])
        ]

        images_by_id: dict[int, CarddImage] = {}
        for img in data.get("images", []):
            entry = CarddImage(
                image_id=int(img["id"]),
                file_name=str(img["file_name"]),
                width=int(img["width"]),
                height=int(img["height"]),
            )
            images_by_id[entry.image_id] = entry

        for ann in data.get("annotations", []):
            img_entry = images_by_id.get(int(ann["image_id"]))
            if img_entry is None:
                continue
            seg = ann.get("segmentation", [])
            if not isinstance(seg, list) or not seg:
                continue
            polygons = self._to_polygons(seg)
            if not polygons:
                continue
            img_entry.annotations.append(
                CarddAnnotation(category_id=int(ann["category_id"]), polygons=polygons)
            )

        images = sorted(images_by_id.values(), key=lambda img: img.image_id)
        return categories, images

    @property
    def split(self) -> str:
        return self._split

    @property
    def root(self) -> Path:
        return self._root

    def categories(self) -> list[CarddCategory]:
        return list(self._categories)

    def category_ids(self) -> list[int]:
        return sorted({c.id for c in self._categories})

    def images(self) -> list[CarddImage]:
        return list(self._images)

    def load_image(self, image: CarddImage) -> np.ndarray:
        """Read an image as RGB. Raises FileNotFoundError on a missing file."""
        path = self._root / self._split / image.file_name
        img = cv2.imread(str(path))
        if img is None:
            raise FileNotFoundError(f"missing image: {path}")
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    def rasterize(self, image: CarddImage) -> np.ndarray:
        """Rasterize all annotations of an image into NxHxW binary masks."""
        masks = np.zeros((len(image.annotations), image.height, image.width), dtype=np.uint8)
        for i, ann in enumerate(image.annotations):
            for polygon in ann.polygons:
                pts = np.asarray(polygon, dtype=np.float32).reshape(-1, 2).astype(np.int32)
                cv2.fillPoly(masks[i], [pts], 1)
        return masks
