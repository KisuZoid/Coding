# Implementation ↔ Research Reconciliation

Status: reconciled on 2026-09-25 against
`AutoInspect-X_Research_Report_Corrected.md`, ADR 0010, ADR 0011, ADR 0012,
and ADR 0013. The runtime catalogue is implemented; the final research
interpretation remains partial.

Legend: `IMPLEMENTED`, `PARTIAL`, `PLANNED`, `REMOVED`, `UNVERIFIED`.

## 1. Photo-first research contract

The research contribution is a CNN–Transformer hybrid segmentation model
(`HybridSegmentation`) compared with a ResNet34 U-Net baseline
(`ResNet34UNet`) for segmentation quality and confidence honesty on CarDD.
The product flow is:

```text
photo → capture-quality gate → segmentation → evidence payload
      → honest explanation → optional consent → grounded chat
```

Repair cost, repair action, hidden-damage prediction, physical cm² area, and
the questionnaire flow are removed under ADR 0011. No synthetic cost table is
used.

## 2. Current model evidence

| Model ID | Architecture | Seed | Status | Best val foreground mIoU | Best epoch |
|---|---|---:|---|---:|---:|
| `final60_baseline_seed42` | ResNet34UNet | 42 | CONTROLLED | 0.6676585078 | 44 |
| `final60_baseline_seed1337` | ResNet34UNet | 1337 | CONTROLLED | 0.6681153178 | 50 |
| `final60_hybrid_seed42` | HybridSegmentation | 42 | CONTROLLED | 0.6701672077 | 49 |
| `final60_hybrid_seed1337` | HybridSegmentation | 1337 | CONTROLLED | 0.6731674075 | 47 |
| `final100_hybrid_seed42` | HybridSegmentation | 42 | EXPLORATORY | 0.6715497971 | 58 |

The four controlled entries are a two-seed comparison under the 60-epoch target
configuration. They do not establish a general architecture ranking. The
final-100 record is a partial reconstructed continuation, not a matched arm or
a completed 100-epoch result.

## 3. Implementation status

### Segmentation and catalogue

- `IMPLEMENTED`: `ResNet34UNet`, `HybridSegmentation`, architecture-tagged
  checkpoint loading, explicit five-model catalogue, `GET /models`, and session
  model selection.
- `IMPLEMENTED`: model-specific engine caching, model ID in analysis response,
  and selection locking after evidence is created.
- `IMPLEMENTED`: legacy `CarddUNet`/`CarddHybrid` loading remains for archival
  checkpoint compatibility; these are not current runtime defaults.
- `IMPLEMENTED`: training/inference separation under ADR 0003.
- `IMPLEMENTED`: the current controlled Dice + Focal objective and
  deep-supervision weights documented in ADR 0013; the CE path is historical.

### Product and evidence

- `IMPLEMENTED`: photo upload, capture-quality gate, predicted mask, class and
  image-relative area features, confidence flags, overlay, assistant grounding,
  consent, and follow-up chat.
- `IMPLEMENTED`: normalized area is a DERIVED FEATURE; predictions remain MODEL
  PREDICTION labels.
- `IMPLEMENTED`: no cost, repair-action, hidden-damage, or cm² output.

### Research evaluation

- `PARTIAL`: current controlled evidence covers two seeds and model-specific
  validation metrics; a third seed is not present.
- `PLANNED`: RQ2 confidence-honesty operational definition and reproducible
  `research_summary.md`.
- `PARTIAL`: external validation and additional ablation work are not present.
- `PARTIAL`: final-100 continuation history is incomplete; only the recorded
  checkpoint evidence may be cited.

## 4. Evidence locations

- Models: `ml/models/resnet34_unet.py`,
  `ml/models/hybrid_segmentation.py`.
- Training: `ml/training/train.py`, `ml/training/loss.py`,
  `ml/training/cardd_dataset.py`.
- Evaluation: `ml/evaluation/evaluate_run.py`, `ml/evaluation/metrics.py`, and
  `ml/evaluation/small_damage.py`.
- Inference: `ml/inference/engine.py` and `ml/inference/features.py`.
- Runtime catalogue: `apps/api/model_catalog.py`,
  `apps/api/container.py`, and `apps/api/routers/models.py`.
- Records: ignored `ml/experiments/*/run_record.json` and
  `ml/experiments/registry.json`.
- Decision records: `docs/decisions/0010-cardd-hybrid-model.md`,
  `docs/decisions/0011-photo-first-scope.md`,
  `docs/decisions/0012-five-model-runtime-catalog.md`, and
  `docs/decisions/0013-dice-focal-catalogue.md`.

## 5. Gaps and claim limits

1. The current values are validation measurements, not a completed statistical
   comparison across three seeds.
2. Small-damage performance and confidence honesty must be reported before
   broad claims about practical reliability.
3. The final-100 directory must retain its partial status; do not fill missing
   epochs from inference or periodic filenames.
4. The hybrid seed-1337 run retains resume metadata; preserve it in any
   reproducibility discussion.
5. The public cinematic frame OCR audit is complete; direct visual
   interpretation was unavailable in the current tool environment.
6. The report, presentation, and literature-review outputs must distinguish
   source statements from current repository measurements.

## 6. Recommended next action

Reconcile the deliverables, run the complete quality gates, then lock the RQ2
metric and decide whether a third controlled seed is required before writing a
comparative conclusion. Do not present the current two-seed values as proof
that one architecture is superior.
