# Phase 10 — Part-Segmentation Decision Record

Date: 2026-09-08. Deliberation required by the Phase 5–12 plan: is vehicle-part
segmentation a hard requirement for the segmentation core?

## Question

The research report's architecture uses a normalized damage-area feature
`normalized_damage_area = damaged_pixels / affected_part_pixels`. CarDD-COCO has
damage masks only (ADR 0005 audit, Phase 1). Computing the denominator needs
vehicle-part masks (hood, bumper, door, fender, wheel arch, ...).

Decision asked by the Phase 10 milestone: adopt a part-mask source (new ADR,
new dataset/licence, preprocessing, part-label mapping, split policy per
`experiment-principles.md` §3) or keep the image-normalized damage-area ratio
and document the gap.

## Evidence considered

| Factor | Finding | Source |
|---|---|---|
| Part masks in CarDD | absent by audit | ADR 0005 |
| Research requirement | `normalized_damage_area` uses part denominator | report §(formula), problem-definition |
| Baseline result (Phase 8/9) | damage under-detected (recall 0.06, small-damage ≈ 0) at 5 epochs | `research_summary.md`, `error_analysis_report.md` |
| Error pattern | FN-dominated; extent/confidence failure persists for large damage too | Phase 9 patterns |

## Decision

**Keep the image-normalized damage-area ratio; do not adopt part segmentation
in this capstone cycle.**

1. **Active non-adoption, not deferral-by-silence.** The Phase 8/9 evidence
   shows the segmentation core itself (any-area feature) is not yet converged;
   part masks would multiply data and pipeline cost while the baseline cannot
   yet localize damage reliably.
2. No new dataset is acquired; ADR 0005's prohibition stands: the research name
   `normalized_damage_area` is not emitted for a different computation. The
   adapter exposes `damage_area_ratio_image` (DERIVED FEATURE) only.
3. If part masks become a requirement in a later cycle, they enter as a new ADR
   with licence, label mapping, preprocessing, deduplication, and
   train/val/test policy — no silent substitution.

## Consequences

- Research-facing documents must not present `damaged_pixels / part_pixels` as
  implemented. `implementation-alignment.md` already lists it as a gap; this
  decision fixes the recommended action to "not adopted this cycle".
- Any future segmenter output continues to report per-class damage areas over
  the image denominator, labelled DERIVED FEATURE.
- Part-aware features (e.g. "bumper dent") remain downstream/optional research
  items, not current deliverables.

## Supersedes / extends

- Extends ADR 0005 (keeps its status Accepted; this record is the Phase 10
  working decision on top of it).