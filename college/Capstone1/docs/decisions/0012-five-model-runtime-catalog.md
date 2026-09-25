# ADR 0012 — Five-model runtime catalogue and partial final-100 record

Status: **Accepted** (2026-09-25).

## Context

The running product had accumulated pilot, legacy, and extended-experiment
references. The inference path also depended on a single `MODEL_PATH` setting,
which made the active model ambiguous and made selecting a checkpoint for a
session impossible. A final-100 hybrid directory contains a best checkpoint and
periodic snapshots, but the available metadata does not establish a completed
100-epoch training history.

The repository contract distinguishes the four matched 60-epoch runs from the
exploratory continuation. Superseded pilot artifacts must remain recoverable
without being treated as current model evidence.

## Decision

1. The runtime catalogue is an explicit five-entry allowlist:
   - `final60_baseline_seed42` — CONTROLLED.
   - `final60_baseline_seed1337` — CONTROLLED.
   - `final60_hybrid_seed42` — CONTROLLED.
   - `final60_hybrid_seed1337` — CONTROLLED.
   - `final100_hybrid_seed42` — EXPLORATORY.
2. `final60_hybrid_seed42` is the product default because it is a measured,
   controlled hybrid checkpoint and avoids presenting the incomplete continuation
   as a completed experiment.
3. `GET /models` publishes the allowlist, availability, architecture, seed,
   checkpoint provenance, and record status. Session creation accepts an
   optional `model_id`; `PATCH /inspection/{session_id}/model` changes the
   selection before analysis and locks it once inspection evidence exists.
4. The engine dispatches architecture from checkpoint metadata. The model ID
   is recorded in the inspection response and engine metadata.
5. `MODEL_PATH` remains supported for a deliberate legacy/custom checkpoint
   configuration, but it is not the normal catalogue path and does not bypass
   the allowlist for catalogue sessions.
6. Active experiment directories retain only `best_checkpoint.pt` and
   `run_record.json`. Pilot directories and their periodic checkpoints are
   archived or removed from live storage.
7. The final-100 run record is explicitly
   `PARTIAL_RECONSTRUCTED_FROM_CHECKPOINTS`; it must not be used to claim a
   completed 100-epoch run, matched comparison, or statistical conclusion.

## Consequences

- Product sessions can be traced to one of five stable model IDs.
- The four controlled 60-epoch runs can be compared without implying that the
  exploratory continuation is a fifth matched arm.
- Missing training history remains visible rather than being filled with
  invented values.
- Legacy pilot references remain available under `archive/experiments/` for
  provenance but are not live defaults.
