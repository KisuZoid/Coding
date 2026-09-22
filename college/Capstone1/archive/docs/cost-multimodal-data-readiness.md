# Phase 11 — Data-Readiness Report: Cost and Multimodal Fields

Date: 2026-09-08. This report classifies every field required by the cost /
multimodal parts of the research question against the data actually held in the
repository, following the ground-truth categories in AGENTS.md §3. Its purpose
is to state, before any implementation, which fields exist as real data, which
are derivable, and which must not be manufactured.

## Scope

Fields checked:

1. Make / model / year / variant
2. Repair location (shop / labor market / region)
3. Repair action (repair / replace / manual inspection)
4. Observed final cost
5. Currency
6. Parts cost
7. Labour cost
8. Damage metadata usable for cost prediction (damage type, area, region)

## Repository data inventory

| Source | Contents | Licence |
|---|---|---|
| CarDD-COCO (v1.0, 2022) | 4000 images; 6 damage classes; per-instance polygon masks, bbox, area; per-annotation `attributes.occluded`; image size. **No metadata, no costs, no repair actions.** | CarDD / USTC (research-use; see CarDD site). Registered in `ml/datasets/cardd_audit.json` (image counts, class stats) |
| Derived code | per-class mask aggregation, damage-area-over-image ratio | — |

No other dataset, CSV, price book, or metadata source is held in or referenced
by the repository.

## Field-by-field classification

| Field | Status | Meaning |
|---|---|---|
| Make | **MISSING** | not present in any source |
| Model | **MISSING** | not present in any source |
| Year / age | **MISSING** | not present in any source |
| Variant / trim | **MISSING** | not present in any source |
| Repair location / region | **MISSING** | not present in any source |
| Repair action | **MISSING** | not present in any source (and cannot be derived from segmentation alone with real evidence; would be a MODEL PREDICTION only) |
| Observed final cost | **MISSING** | not present in any source |
| Currency | **MISSING** (implied only by region of dataset, which itself is unstated) | not a field; cannot be asserted |
| Parts cost | **MISSING** | not present in any source |
| Labour cost | **MISSING** | not present in any source |
| Damage type (6 classes) | **REAL GROUND TRUTH** | CarDD polygons, category ids |
| Per-instance area (px) | **DERIVED FEATURE** | computed from masks; image-normalized ratio only (ADR 0005) |
| Damage location (image coords region) | **REAL GROUND TRUTH** (as annotated) / DERIVED FEATURE (centroid etc.) | bbox + masks; keep distinction |
| `occluded` attribute | **REAL GROUND TRUTH** | present in annotation schema but unused to date |

## Conclusion

- **Observed cost labels: MISSING.** Per the plan and AGENTS.md §3, cost-model
  implementation **stops here**. No rule-generated cost table may be presented
  as real repair-cost ground truth; a rule-generated table is a SYNTHETIC
  LABEL at best and must be labelled as such if ever produced.
- The **multimodal feature sources are also MISSING**: no metadata file exists
  to fuse with vision features. Any "fusion" experiment would therefore be
  against fabricated inputs and is not warranted yet.
- What *can* meaningfully proceed from this inventory is the **vision-only
  baseline** path (already run: `cardd_baseline_ce`) and the segmentation-core
  experiments, plus the explainability value of the segmentation masks.

## Recommended next actions (blocking conditions)

| Item | Condition to start |
|---|---|
| Cost head / cost experiment | real observed cost labels (or an explicitly-labelled SYNTHETIC study with rationale + ADR) |
| Multimodal fusion (B1/B2/P) | a real metadata source for make/model/year/variant/location/action |
| Repair-action classifier | a labelled repair-action source |
| Part-aware damage features | real part-mask source (ADR 0009: not adopted this cycle) |

Until one of the blocking conditions is met, the research pipeline's image
side (segmentation → per-class damage features → damaged-area-over-image ratio)
is the only fully-supported path, matching the Phase 10 decision and
`implementation-alignment.md`.

## Risks

1. Market-price or repair-cost figures appear in the research report (§cost
   section). They are **report-provided, unverified figures**, not repository
   data; the report was never a data source for training and must not be
   treated as one (citation-integrity note in `implementation-alignment.md`).
2. A reviewer may assume CarDD ships metadata because "damage datasets usually
   do". This report is the factual counter-evidence: verified by direct
   inspection of `instances_train2017.json` on 2026-09-08.