# LOGIC.md — AutoInspect-X

Logic of the project pipeline, workflows, and automations. Update this file
whenever the decision logic of the system changes — not only when code changes.

---

## 1. Status

- **Application logic implemented:** none. The repository holds documentation and
  configuration only.
- **n8n workflows:** none. No n8n MCP server is configured and the n8n CLI is not
  installed on this machine. See `init.md` §4 for how to verify this.
- **Form automations:** none.
- **Scheduled jobs / webhooks:** none.

Everything below section 2 describes intended logic, not implemented behaviour.
Do not describe it to anyone as working software.

---

## 2. Core inference logic (intended)

```
1. Image intake
   Vehicle photograph(s) are uploaded with vehicle metadata.

2. Segmentation
   A segmentation model produces per-pixel masks for damage regions and for
   vehicle parts.

3. Damage representation
   From the masks, derive per-damage-region features:
     - damage type            (model prediction)
     - damage area ratio      (derived feature: damaged pixels / part pixels)
     - location on the vehicle(derived feature)
     - affected part          (model prediction)
     - segmentation confidence(model output)
     - geometry descriptors   (derived feature)

4. Metadata encoding
   make, model, year or age, and region are encoded as structured features.

5. Multimodal fusion
   Damage representation and metadata features are fused.

6. Heads
   a. Repair action  → repair / replace / manual inspection
   b. Repair cost    → lower, median, upper quantile estimates

7. Explainable report
   Present the visual evidence that drove the prediction, alongside the
   uncertainty range.
```

### Labelling rules that constrain this logic

- The damage area ratio is a **normalized ratio**, never a physical measurement
  in cm². An uncontrolled photograph carries no scale reference.
- Repair-cost values derived from a rule or price table are a **SYNTHETIC
  LABEL**, never REAL GROUND TRUTH.
- Hidden-damage risk is out of scope unless real ground-truth labels exist.
- The output is an **AI estimate and decision support**, never a final
  professional workshop quotation. The interface must state this.

---

## 3. Intended product flow (demo narrative)

```
1. Upload vehicle image
2. Model identifies the damaged region
3. Show the segmentation overlay
4. Show damage type and severity features
5. Add vehicle information
6. Generate a preliminary repair-cost range
7. Show uncertainty and confidence
8. Explain which visual evidence influenced the result
9. Export the inspection report
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
never required on CI (tests use the rule-based Groq service).

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
