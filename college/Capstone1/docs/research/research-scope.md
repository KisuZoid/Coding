# Research Scope

> **Provisional** until `AutoInspect-X_Research_Report_Corrected.md` is added to
> the repository. Reconcile then.

## In scope

| Component | Scope |
|---|---|
| Damage / part segmentation | Per-pixel masks for damage regions and vehicle parts |
| Damage representation | Type, normalized area ratio, location, affected part, model confidence, geometry descriptors |
| Metadata encoding | Make, model, year or age, region |
| Multimodal fusion | Combining the damage representation with encoded metadata |
| Repair-action prediction | repair / replace / manual inspection |
| Cost estimation | Quantile estimates: lower, median, upper |
| Explainability | Visual evidence linking prediction to segmented region |

## Out of scope

| Excluded | Reason |
|---|---|
| Hidden-damage risk | No real ground-truth labels exist |
| Physical area in cm² | No scale reference in an uncontrolled photograph |
| Final workshop quotation | Requires parts pricing, labour rates, and a human assessor |
| Vehicle identification from the image | Metadata is user-supplied |
| Fraud detection | Different problem, different data |

## Claim boundaries

These constraints bind every paper, report, slide, and interface string:

1. A rule-generated cost table is a **SYNTHETIC LABEL**, never REAL GROUND TRUTH.
2. A normalized damage-area ratio is not a physical measurement.
3. A model prediction is not evidence of physical damage severity.
4. An improvement claim requires a measured comparison against both the
   vision-only and simple-fusion baselines, on the same splits and seeds.
5. Generalisation claims are bounded by the datasets actually used — their
   regions, vehicle segments, lighting conditions, and camera characteristics.

## Metrics

The research document is the authority on the final metric set. Working
expectation, to be confirmed:

| Task | Candidate metrics |
|---|---|
| Segmentation | IoU / mIoU, Dice, per-class breakdown |
| Repair action | Accuracy, macro F1, confusion matrix |
| Cost estimation | MAE, MAPE, pinball loss, interval coverage, interval width |
| Uncertainty | Calibration of the predicted interval against realised error |

Interval coverage matters as much as point accuracy. A cost range that is narrow
and wrong is worse than a wide range that is honest.

## Deliverables

1. Reproducible experiments comparing the proposed model against both baselines.
2. A working prototype demonstrating upload → segmentation → damage features →
   estimate → explanation → report.
3. Documentation of datasets, licences, preprocessing, splits, and limitations.
