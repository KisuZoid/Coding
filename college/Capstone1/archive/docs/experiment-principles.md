# Experiment Principles

Rules that make every experiment in this project reproducible and honest. They
apply from the first experiment onward, not once results start looking good.

## 1. Record for every run

| Field | Notes |
|---|---|
| Experiment ID | Stable, unique, referenced by every artefact of the run |
| Dataset and version | Including any filtering applied |
| Split strategy | How train / validation / test were constructed |
| Random seed | Every source of randomness |
| Code version | Git commit hash, on a clean working tree |
| Model version | Architecture and checkpoint identifier |
| Hyperparameters | Complete, not just the ones that were tuned |
| Metrics | The full set, not only the favourable ones |
| Evaluation outputs | Predictions, confusion matrices, plots |
| Assumptions | Anything chosen rather than measured |

A run that cannot be reproduced from its record is not a result.

## 2. Data hygiene

- Never mix training and test data.
- Split **before** any preprocessing that uses dataset statistics.
- Avoid image-level leakage: near-duplicate photographs, multiple angles of the
  same vehicle, and re-uploads of the same incident must not straddle splits.
  Group by vehicle or incident identifier, not by image.
- Deduplicate before splitting, and record how duplicates were detected.
- The test split is touched once, at the end. Model selection uses validation.

## 3. Combining datasets

Document for each source:

- origin and URL;
- licence, and whether the intended use is permitted;
- preprocessing applied;
- class label mapping into this project's taxonomy;
- filtering rules and how many samples each removed;
- deduplication method;
- how the source contributes to train, validation, and test.

Label taxonomies rarely align between sources. Record the mapping explicitly —
a silent merge of two different definitions of "dent" invalidates the results.

## 4. Baselines

Every claim of improvement is measured against:

1. a vision-only baseline;
2. a simple-fusion baseline.

Baselines run on the same splits, the same seeds, and the same metric code as
the proposed model. A baseline that was not tuned with comparable effort is not
a fair comparison, and the report must say how much tuning each received.

## 5. Uncertainty

Cost estimation outputs an interval. Evaluate the interval, not only the point
estimate:

- empirical coverage against the nominal level;
- interval width — a wide interval that always covers is not automatically good;
- calibration across the cost range, since errors on cheap and expensive repairs
  behave differently.

## 6. Reporting

- Report seeds and variance across runs, not a single favourable run.
- Report failure cases alongside successes.
- State every limitation that follows from the data actually used.
- Never present a SYNTHETIC LABEL result as validation against reality. If cost
  labels come from a rule table, the experiment measures agreement with that
  rule, and the report must say exactly that.
