# ADR 0003 — Training and inference are separate code paths

- **Status:** Accepted
- **Date:** 2026-09-07

## Context

The same models are used for research experiments and for the product demo. The
tempting shortcut is to import training modules into the API so a checkpoint can
be loaded with the code that produced it.

## Decision

Training code (`ml/training/`) and inference code (`ml/inference/`) are separate.
The API depends on the inference layer only. The interface between them is a
versioned model artefact plus its metadata: version, training run ID, input
contract, output contract.

Model location comes from configuration (`MODEL_PATH`, `MODEL_VERSION`), never
from a hard-coded path.

## Rationale

- Training dependencies are heavy and often GPU-bound. Pulling them into the API
  makes deployment fragile and slow.
- A shared import path means an experiment refactor can silently change
  production behaviour.
- An explicit artefact contract makes it possible to state exactly which model
  produced a given result — a reproducibility requirement.
- The API can be tested against a stubbed inference layer without a training
  environment.

## Consequences

- Preprocessing used at training time must be reproduced in the inference path.
  This is a real risk of skew, and is mitigated by keeping preprocessing in a
  shared, version-pinned module that both paths import, rather than by
  duplicating the logic.
- Publishing a model becomes an explicit step: export the artefact, record its
  metadata, update the configured version.
- A missing or mismatched artefact fails loudly at startup. There is no fallback
  prediction, because a silent fallback would produce confident wrong output.
