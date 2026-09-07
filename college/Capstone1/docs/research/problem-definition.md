# Problem Definition

> **Provisional.** The research document
> `AutoInspect-X_Research_Report_Corrected.md` is not yet in this repository.
> Everything here is derived from the project bootstrap brief alone. When the
> research document arrives, reconcile this file against it and record any
> material difference as an ADR.

## Problem

Estimating vehicle repair cost from photographs is currently manual, slow, and
inconsistent between assessors. An automated preliminary estimate would support
insurance triage, workshop intake, and used-vehicle assessment — provided it is
presented as decision support and not as a binding quotation.

Two decisions matter in practice:

1. **Repair action** — repair, replace, or escalate to manual inspection.
2. **Repair cost** — a range, not a point estimate, because photographs cannot
   reveal everything a physical inspection would.

## Research question

Can segmentation-derived damage representations, combined with vehicle metadata,
improve repair-cost estimation and repair-action prediction compared with
vision-only and simple-fusion baselines?

## Why segmentation rather than classification

A classifier answers "is this vehicle damaged, and how badly". Segmentation
answers "which part, how much of it, and where" — producing a structured damage
representation that can be fused with metadata and, critically, shown to the
user as visual evidence. Explainability is a project requirement, not a bonus.

## Inputs

| Input | Type | Source |
|---|---|---|
| Vehicle photograph(s) | image | user upload |
| Make, model, year or age, region | structured | user-provided metadata |

## Outputs

| Output | Form |
|---|---|
| Repair action | repair / replace / manual inspection |
| Repair cost | lower, median, upper quantile estimates |
| Explanation | segmentation overlay plus the damage features that drove the result |

## Baselines to beat

1. **Vision only** — image features straight to the prediction heads, no metadata.
2. **Simple fusion** — image embedding concatenated with metadata, with no
   structured damage representation.

The contribution claim depends on the proposed model beating both. Until that
comparison is run, no improvement may be claimed.

## Out of scope

- **Hidden-damage risk prediction.** Excluded unless real ground-truth labels
  become available. Synthetic hidden-damage labels do not qualify.
- **Physical damage area in cm².** An uncontrolled photograph has no scale
  reference. Only a normalized damage-area ratio is defensible.
- **Final workshop quotation.** The system produces an estimate. The interface
  must state the difference.

## Open questions

1. Which segmentation dataset, under which licence?
2. What is the real source of repair-cost labels? If costs come from a rule or
   price table, they are a SYNTHETIC LABEL and every claim must say so.
3. How is the repair-action label defined, and by whom?
4. Which regions and vehicle segments does the data actually cover, and what does
   that mean for the generalisation claim?
