# ADR 0005 — CarDD provides no vehicle-part masks: normalized_damage_area handling

- **Status:** Accepted
- **Date:** 2026-09-08

## Context

The damage representation required by the research pipeline includes a
normalized damage-area ratio. The proposed definition is

```
normalized_damage_area = damaged_pixels / affected_part_pixels
```

The audit of the working dataset (CarDD-COCO, ADR 0004 policy / Phase 1 audit)
established that CarDD provides **damage masks only**. It contains **no vehicle-part
masks** (no per-part annotation of hood, bumper, door, fender, and so on).
Applying the formula therefore needs a part-mask source that CarDD does not
supply.

This gap affects which area feature the Phase 2 adapter and all later training
can honestly produce. ADR 0004 already forbids claiming physical area in cm²; this
record extends that to the normalized ratio itself until a part source exists.

## Decision

1. The Phase 2 CarDD adapter produces a **damage-area-over-image ratio**
   (`damaged_pixels / total_image_pixels`) as the only area feature derived from
   CarDD alone. It is a DERIVED FEATURE and is labelled as such everywhere.
2. The research formula `normalized_damage_area = damaged_pixels / part_pixels`
   is **not implemented** and is **not reported** from any CarDD-only source. Any
   code, figure, or interface that appears to compute it must be treated as
   incorrect.
3. If vehicle-part segmentation becomes a requirement later (it is not today in
   `docs/research/`), the part-mask source must be adopted as its own ADR with
   licence, label mapping, preprocessing, and split policy — mirroring the rules
   in `docs/research/experiment-principles.md` §3.

## Rationale

- Fabricating part masks or silently substituting a whole-image denominator
  would misstate the research feature and violate ADR 0004 (categories must stay
  distinct; DERIVED FEATURE is computed from other data, not observed).
- A damaged-pixels-over-image ratio is defensible, computable from CarDD alone,
  and keeps the area feature honest without a part source.
- Keeping the door open via a future ADR preserves the research possibility
  without committing to an unfounded data source now.

## Consequences

- ML features derived from masks must name the denominator explicitly
  (e.g. `damage_area_ratio_image`), never reuse the research name
  `normalized_damage_area` for a different computation.
- Tests may assert that the adapter exposes only the image-denominator ratio.
- If real part masks are added later, this ADR is superseded by a new record, and
  previously reported area ratios are re-expressed or retired — not silently
  reinterpreted.