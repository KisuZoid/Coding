"""CarDD damage class map for inference (Phase D).

Transcribed verbatim from the CarDD-COCO category table
(``datasets/CarDD_COCO/annotations/instances_*.json``). Channel 0 is
background: ADR 0008 trains and decodes with a per-pixel ``argmax`` over all
7 channels, where background wins channel 0 when no damage class is dominant.
The product must only ever report these canonical CarDD names, never invented
category labels.
"""

from __future__ import annotations

from collections.abc import Iterable

NUM_CLASSES = 7
BACKGROUND_CLASS = 0

ID_TO_CLASS: dict[int, str] = {
    0: "background",
    1: "dent",
    2: "scratch",
    3: "crack",
    4: "glass shatter",
    5: "lamp broken",
    6: "tire flat",
}

CLASS_TO_ID: dict[str, int] = {name: cid for cid, name in ID_TO_CLASS.items()}

DAMAGE_CLASS_IDS: tuple[int, ...] = tuple(cid for cid in ID_TO_CLASS if cid != BACKGROUND_CLASS)


def validate_class_ids(class_ids: Iterable[int]) -> None:
    """Reject class ids that are not in the CarDD contract."""
    unknown = sorted({cid for cid in class_ids if cid not in ID_TO_CLASS})
    if unknown:
        raise ValueError(f"class ids not in CarDD contract: {unknown}")
