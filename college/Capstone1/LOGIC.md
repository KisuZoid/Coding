# LOGIC.md — AutoInspect-X

Logic of the project pipeline, workflows, and automations. Update this file
whenever the decision logic of the system changes — not only when code changes.

---

## 1. Status

- **Application logic implemented:** photo-first inspection API — session
  creation, upload, analyze (capture-quality gate + segmentation + assistant
  explanation), optional consent, and chat follow-ups (ADR 0011). See
  `docs/architecture/overview.md`.
- **Assistant:** LangChain `ChatGroq` when `GROQ_AUTO_INSPECT_API_KEY` is set
  (`build_assistant`, model from `settings.groq_model` / `GROQ_MODEL`);
  otherwise a deterministic offline `StubAssistant`.
- **n8n workflows:** none. No n8n MCP server is configured and the n8n CLI is not
  installed on this machine. See `init.md` §4 for how to verify this.
- **Form automations:** none.
- **Scheduled jobs / webhooks:** none.

Section 2 describes implemented behaviour; section 4 describes future
automation contracts, not existing workflows. Do not describe those to anyone
as working software.

---

## 2. Core inspection logic (implemented)

```
1. Session creation
   POST /inspection/session — one session id, owned by the user.

2. Photo upload
   POST /inspection/<id>/upload — the photo is validated, EXIF-stripped, and
   ledgered for the session. A new upload supersedes the previous one.

3. Analysis — POST /inspection/<id>/analyze
   a. Capture-quality gate (blur / dark / glare / contrast / framing). On
      rejection the endpoint returns HTTP 200 with
      status="QUALITY_FAILED" and writes the assistant's retake guidance into
      the conversation; no mask is produced and no model inference runs.
   b. Segmentation — the engine (CarddHybrid by default; dispatch on the
      checkpoint's model_arch key, ADR 0010) returns per-pixel logits; argmax
      over background + 6 CarDD classes.
   c. Evidence payload — classes present, image-denominator area ratios, mean
      confidence, low-confidence flag, quality outcome, model metadata; the
      predicted-mask overlay is stored and served.
   d. Assistant explanation — the assistant service explains the evidence as
      the first assistant message in the conversation. The LLM is a
      **non-blocking stage** of /analyze: if the live LangChain/Groq call fails,
      the endpoint still returns the full structured result with
      `assistant_fallback=true` (a clearly offline, deterministic evidence
      summary), never a 503. The real exception is logged server-side.

4. Optional consent — POST /inspection/<id>/consent
   GRANTED stores an anonymised training sample with MODEL_SUGGESTED
   provenance (features from the summary; placeholder mask — never claimed as
   validated evidence). DECLINED records the decision only.

5. Follow-up chat — POST /chat
   A LangGraph turn (START -> llm_turn -> END) appends the user message and
   asks the assistant service (LangChain ChatGroq, or the offline
   StubAssistant) for a reply grounded in the persisted, prompt-safe evidence.
   ChatResponse has no waiting_for/finished fields: there is no questionnaire
   gating. Ordinary chat never touches the segmentation engine, so it works
   with or without a prior analysis; a dead LLM is a typed `503 LLM_UNAVAILABLE`.

### Error contract (typed, safe)

The API never collapses distinct failures into one message. `detail` is always
`{"code": ..., "message": ...}` where `code` ∈ `SESSION_NOT_FOUND`,
`SESSION_CLOSED`, `SESSION_EXPIRED`, `NO_UPLOADED_PHOTO`, `BAD_UPLOAD`,
`MODEL_UNAVAILABLE` (engine could not be built), `INFERENCE_FAILED` (forward
pass failed), `LLM_UNAVAILABLE`. Responses never contain tracebacks, keys, or
internals; real exceptions are preserved in the backend logs (uvicorn
`logger.exception`).
```

### Labelling rules that constrain this logic

- The damage area ratio is an **image-denominator normalized ratio**, never a
  physical measurement in cm². An uncontrolled photograph carries no scale
  reference.
- The overlay and per-class damage labels are **MODEL PREDICTIONS**, never
  verified damage extent; `low_confidence` results are presented as preliminary.
- Repair-cost and repair-action prediction were removed from scope (ADR 0011);
  no synthetic cost labels exist anywhere in code, data, or UI.
- Hidden-damage risk is out of scope unless real ground-truth labels exist.
- The output is an **AI inspection / decision support**, never a final
  professional workshop quotation. The interface must state this.

---

## 3. Demo flow (as users experience it)

```
1. Open the demo — the composer accepts a photo attachment (preview, remove, send).
2. Attach and send a photo of the damage.
3. The backend runs the capture-quality gate.
4. On rejection — retake guidance appears in the assistant bubble; no mask.
5. On success — the predicted-mask overlay, class chips, area ratio and
   confidence render inline, with honesty annotations when low confidence.
6. Optionally grant or decline training consent (inline under the chat).
7. Ask follow-up questions; answers stay grounded in the stored evidence.
8. The session ends when it expires or is deleted; nothing else is produced.
```

---

## 4. Automation — the contract for any future workflow

No automation exists yet. When one is added, it must be documented here before
being considered complete, using this template:

```
### Workflow: <name>
**Platform:** n8n | GitHub Actions | cron | other
**Trigger:** webhook | schedule | form submission | manual
**Owner:** who maintains it
**Inputs:** payload shape and where it comes from
**Steps:** numbered, one action per step
**Outputs:** what it writes, and where
**Credentials:** which environment variables it needs (names only, never values)
**Failure behaviour:** retries, dead-letter handling, alerting
**Idempotency:** what happens if the same event arrives twice
```

Placement rules:

| Concern | Location |
|---|---|
| Exported n8n workflow JSON | `automation/n8n/` |
| Workflow logic and data contracts | this file |
| Webhook endpoints consumed by a workflow | `apps/api/`, documented here |
| Credentials | environment variables only, never committed |

A form automation, if it is built, must also record: which form, where
submissions land, what validation runs, and what the user-visible confirmation
is.

---

### Workflow: CI — backend gates, frontend gates, Playwright browser E2E

**Platform:** GitHub Actions (per-repository workflow)

**Trigger:** `push` / `pull_request` (any branch)

**Owner:** repository maintainers (no external credentials)

**Inputs:** the repository at the pushed/PR commit. No secrets — the backend
runs with CPU runtime deps pinned in `requirements-ci.txt`; the Groq key is
never required on CI (tests blank it in `tests/conftest.py` and use the
deterministic offline `StubAssistant`).

**Steps:**

1. **backend — gates** (ubuntu-latest): checkout; Python 3.12; `uv sync --group dev` +
   `uv pip install --python .venv -r requirements-ci.txt`; then
   `ruff check apps/ ml/ tests/ conftest.py`, `ruff format --check …`,
   `mypy apps/ ml/ tests/` (strict), `pytest tests/`. The committed demo
   checkpoint is git-ignored, so the real-engine test skips exactly as it does
   locally — skipping is a known-and-documented state, never a failure.
2. **frontend — gates** (ubuntu-latest, cwd `apps/web`): `npm ci`; `npm run lint
   -- --max-warnings=0`; `npm run typecheck`; `npm run build`.
3. **e2e — Playwright** (ubuntu-latest, `needs: [backend, frontend]`, cwd
   `apps/web`): backend venv installed and put on `PATH`; `npm ci`; `npm run
   build`; `npx playwright install chrome`; `npx playwright test` with
   `BACKEND_CMD` exported so the Playwright config starts `uvicorn` from the CI
   venv instead of the default conda launcher. The config's `webServer` starts
   backend (:8000) and `next start` (:3000).

**Outputs:** a green/critical summary per commit; no artefacts are published.

**Credentials / environment variables used:**

- `BACKEND_CMD` (workflow `env`, e2e job) — overrides the Playwright config's
  default backend launcher; contains no secrets.
- `GROQ_AUTO_INSPECT_API_KEY` is intentionally **not** set on CI.

**Failure behaviour:** a job failure marks the commit red; retries via `retries`
are not configured — a rerun is manual. No alerting/dead-letter handling is
needed (pure evaluation, no side effects).

**Idempotency:** safe to re-run — build outputs (`.next`, venv) are ephemeral
per-run; the only persistent writes would be storage/training dirs, which live
in fresh CI checkouts.
