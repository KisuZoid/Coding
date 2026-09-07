# ML Engineering Guidelines

## 1. Separation of training and inference

```
Dataset → Preprocessing → Training → Evaluation → Model artefact → Inference API
```

- Training code lives in `ml/training/`, inference code in `ml/inference/`.
- The API imports the inference layer only. It never imports training code, and
  never imports a training dependency at runtime.
- The boundary between them is the **model artefact plus its metadata**: version,
  training run ID, input contract, and output contract.

## 2. Configuration

Never hard-code:

- dataset paths;
- checkpoint paths;
- model versions;
- secrets;
- experiment hyperparameters.

Dataset and experiment settings come from versioned config files under
`ml/experiments/`. Deployment settings come from environment variables
(`MODEL_PATH`, `MODEL_VERSION`). A path written into a source file cannot be
reproduced on another machine and cannot be varied across an experiment sweep.

## 3. Data handling

- Large data never enters Git. `ml/datasets/` holds documentation — source,
  licence, schema, preprocessing, statistics — not the data itself.
- Record how to obtain and prepare each dataset so another person can rebuild it.
- Preprocessing is deterministic and versioned. If preprocessing changes, the
  dataset version changes.
- Deduplicate before splitting, and split by vehicle or incident, not by image.

## 4. Damage representation

Derived from segmentation masks, per damage region:

| Feature | Category | Note |
|---|---|---|
| Damage type | MODEL PREDICTION | Carries model confidence |
| Damage area ratio | DERIVED FEATURE | Damaged pixels ÷ part pixels. Normalized, unitless |
| Location on vehicle | DERIVED FEATURE | Relative to the segmented part |
| Affected part | MODEL PREDICTION | Carries model confidence |
| Segmentation confidence | MODEL PREDICTION | Propagate downstream; do not discard |
| Geometry descriptors | DERIVED FEATURE | Shape statistics of the mask |

Do not convert the area ratio into cm². An uncontrolled photograph carries no
scale reference, and camera distance changes apparent size. If physical area is
ever required, it needs an explicit calibration method, documented and validated.

## 5. Label integrity

Carry the label category through code, storage, and the interface:

| Category | Example in this project |
|---|---|
| REAL GROUND TRUTH | Human-annotated segmentation mask |
| WEAK LABEL | Severity inferred from a free-text claim description |
| SYNTHETIC LABEL | Repair cost produced by a rule or price table |
| DERIVED FEATURE | Damage area ratio |
| MODEL PREDICTION | Predicted repair action |
| ASSUMPTION | A chosen labour rate |

A column named `repair_cost` must make its category explicit — in the schema, in
the dataset documentation, and in any figure that uses it.

## 6. Model artefacts

- Never commit checkpoints. Store them outside Git and reference them by version.
- Every artefact records: training run ID, dataset version, code commit, metric
  summary, and input/output contract.
- Loading a model from an unverified source is a security risk; see `SECURITY.md`.

## 7. Evaluation

- Evaluation runs as an explicit experiment, never as part of the application
  test suite.
- GPU training never runs in CI.
- The metric implementation is shared between the baselines and the proposed
  model — one code path, so a metric bug affects all arms equally.
- Report interval coverage and width for cost estimation, not only point error.

## 8. Inference in production

- Load the model once at startup, not per request.
- Validate input images at the boundary: type, size, dimensions.
- Return the confidence and the interval alongside every prediction. A point
  estimate with no uncertainty misrepresents what the system knows.
- Fail loudly on a missing or version-mismatched artefact. Never fall back to a
  hard-coded prediction.

## 9. Reproducibility

- Seed every source of randomness and record the seed.
- Pin dependency versions for any run that appears in the report.
- Run experiments from a clean working tree so the commit hash means something.
