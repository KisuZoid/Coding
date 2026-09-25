# Problem Definition

Reconciled against `AutoInspect-X_Research_Report_Corrected.md`, ADR 0010,
ADR 0011, ADR 0012, and ADR 0013.

## Problem

Vehicle damage assessment from a photograph is manual, slow, and dependent on
the assessor. A photo-first system can provide useful decision support, but it
must distinguish a predicted mask from verified damage and must not imply
physical scale, hidden damage, repair action, or cost.

The current system answers:

> Where does the selected segmentation model predict visible damage in this
> image, and how confident is that prediction?

The image-relative area ratio is a derived feature, not a physical measurement.

## Research question

How does the CNN–Transformer hybrid (`HybridSegmentation`) compare with a
ResNet34 U-Net baseline (`ResNet34UNet`) for damage-segmentation quality and
confidence honesty on CarDD under the recorded split, seed, and training
contract?

The current catalogue contains two controlled seeds (`42`, `1337`) for each
architecture. It is a two-seed comparison, not a completed three-seed study.
The `final100_hybrid_seed42` continuation is exploratory and has only a
partially reconstructed record.

## Why segmentation

A classifier can say whether a vehicle is damaged but does not show where each
class appears. Segmentation produces a structured visual representation:
predicted classes, their image-relative proportions, confidence, and an
overlay. These outputs are useful for inspection support while remaining
explicitly labelled predictions.

## Inputs

| Input | Type | Source |
|---|---|---|
| Vehicle photograph | image | User upload in the chat composer |
| Optional user text | text | Conversational context only |

Vehicle metadata, insurance data, and questionnaire fields are not model inputs
in the current scope.

## Outputs and evidence labels

| Output | Form | Category |
|---|---|---|
| Damage mask | 7-channel argmax: background + six damage classes | MODEL PREDICTION |
| Per-class area | `damaged_pixels / total_image_pixels` | DERIVED FEATURE |
| Confidence | Mean pixel confidence and `low_confidence` flag | MODEL PREDICTION |
| Overlay | Predicted mask rendered over the photo | MODEL PREDICTION |
| Explanation | Assistant narrative grounded in stored evidence | MODEL PREDICTION / ASSUMPTION on framing |
| Consent sample | Optional stored sample with model-suggested provenance | Not validated ground truth |

CarDD annotations are REAL GROUND TRUTH for dataset evaluation. The system
does not emit repair cost, repair action, workshop quotation, hidden-damage
probability, or physical area in cm².

## Current comparison arms

| ID | Design | Status | Best val foreground mIoU | Best epoch |
|---|---|---|---:|---:|
| `final60_baseline_seed42` | ResNet34UNet, seed 42 | CONTROLLED | 0.6676585078 | 44 |
| `final60_baseline_seed1337` | ResNet34UNet, seed 1337 | CONTROLLED | 0.6681153178 | 50 |
| `final60_hybrid_seed42` | HybridSegmentation, seed 42 | CONTROLLED; default | 0.6701672077 | 49 |
| `final60_hybrid_seed1337` | HybridSegmentation, seed 1337 | CONTROLLED | 0.6731674075 | 47 |
| `final100_hybrid_seed42` | HybridSegmentation, seed 42, continuation | EXPLORATORY | 0.6715497971 | 58 |

The four controlled entries use the 60-epoch target configuration and the two
available seeds. The final-100 entry is not a matched comparison and must retain
`record_status: PARTIAL_RECONSTRUCTED_FROM_CHECKPOINTS`.

## Open questions

1. What exact operational metric will define RQ2 confidence honesty?
2. Is a third controlled seed required before making a comparative claim?
3. How should the small-damage slice and per-class performance be reported for
   the current two-seed evidence?
4. Can any external dataset be adopted only after licence, label mapping,
   deduplication, and leakage policy are documented?

## Out of scope

- Repair-cost and repair-action prediction.
- Hidden-damage risk without real teardown ground truth.
- Physical damage area in cm² from an uncontrolled photograph.
- Vehicle-part segmentation for this cycle.
- Final workshop quotation.
