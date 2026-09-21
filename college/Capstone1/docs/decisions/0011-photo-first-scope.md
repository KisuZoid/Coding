# ADR 0011 — Photo-first scope: remove repair-cost prediction and the questionnaire flow

Status: **Accepted** (2026-09-21). Replaces the "uncertainty-aware repair cost
estimation" product framing. The research direction change and its rationale
are recorded in `AUTOINspectX_PROJECT_STATE.md`; this ADR records the concrete
code, contract, and data consequences.

## Context

Cost/repair prediction was never backed by real ground truth: CarDD carries no
repair costs, and a rule-generated cost table is synthetic, not observed data
(ground-truth policy, ADR 0004). The supervisor cut cost/repair from scope, and
the steer toward a genuine research contribution (photo-first analysis with a
hybrid CNN+Transformer model) removed the questionnaire-driven conversation
(incident → part → city → insurance) that existed only to feed the cost model.
The UI was a multi-panel dashboard; the desired UX is a ChatGPT-style chat with
the photo attached in the composer and results inline.

## Decision

**Scope cut.** All repair-cost and repair-action prediction and the
questionnaire gating are removed:

1. **Deleted modules**: `apps/api/cost/`, `apps/api/repair/`
   (`repair_estimator.py`), `apps/api/agent/groq_service.py`, the `REPAIR_*` /
   `NO_REPAIR` / cost schema fields, `RepairPayload`, `CostPayload`,
   `ALLOW_SYNTHETIC_ESTIMATE` (settings and RUNBOOK), and the `p10/p50/p90`
   demo-only structure. No cost/quote/amount field may appear in any API
   response, persisted state, or UI string (enforced by tests, e.g.
   `_assert_no_forbidden_fields` in `tests/test_e2e_integration.py`).
2. **Photo-first flow**: `POST /inspection/session` → `POST upload` → `POST
   analyze` → optional `POST consent` + `POST /chat`. `analyze` runs the
   capture-quality gate (ADR 0007): on rejection it writes the assistant's
   retake guidance into state and returns `200` with
   `status="QUALITY_FAILED"` (never a mask, never a 422); on acceptance it
   segments, stores an inspection payload (classes, area ratios, confidence,
   quality, model metadata, overlay PNG) and returns `200` with
   `status="OK"`.
3. **Contract simplification**: `ChatResponse` drops `waiting_for`/`finished`;
   `InspectionState` drops questionnaire fields
   (`incident*`, `optional_cursor`, `waiting_for`, `halt`, `finished`,
   `comparison`, `repair`, `cost`).
4. **Assistant**: a single `AssistantService` protocol with `damages_explanation`,
   `retake_guidance`, `chat_reply`. Production impl `LangChainGroqAssistant`
   wraps LangChain `ChatGroq` (model `llama-3.3-70b-versatile`,
   `settings.groq_model`); offline/CI uses `StubAssistant`
   (deterministic, no network, clearly a stand-in). `build_assistant` returns
   the chain when a Groq key is set, else the stub.
5. **Frontend**: ChatGPT-style single-column demo; the composer accepts a photo
   attachment (preview, remove, send); analysis results (overlay + class chips +
   honesty annotations) render inline in the assistant bubble; consent moves
   inline under the chat; the PhotoBay/ContextCard/ResultBlocks side panels are
   deleted. Playwright specs rewritten to the composer flow.

## Ground-truth implications

- The overlay is always the model's *predicted* mask; area ratios stay
  image-denominator (a normalized ratio, not cm²) — unchanged contract.
- Consent samples still store only model_SUGGESTED provenance features and a
  placeholder mask (`features_from_summary`), never claimed as validated
  evidence.
- Removing cost/repair eliminates the only synthetic label family in the API;
  no real-cost claims exist anywhere.

## Consequences

- API and UI shrink and become honest by construction (no cost fields to
  mislabel).
- Chat is stateless turn-wise beyond the stored state; follow-up replies are
  grounded in the persisted inspection evidence via `persist_evidence`
  (base64 payloads stripped from any prompt).
- Tests were rewritten to drive the new contract: `test_e2e_integration.py`
  (photo-first journey, quality-fail guidance, no-forbidden-fields sweeps,
  engine-failure 500, consent), `test_agent_assistant.py`,
  `test_agent_graph.py`, `test_inspection_context.py`, `test_api_settings.py`,
  plus `tests/conftest.py` which blanks the Groq key so the suite is
  deterministic and offline.
- The committed demo checkpoint contract moves to `cardd_hybrid_ce` (see ADR
  0010); the real-engine journey test skips (not fails) until that artefact is
  trained.