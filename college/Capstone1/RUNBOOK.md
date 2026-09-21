# RUNBOOK.md — AutoInspect-X

How to run every part of AutoInspect-X locally on the AI workstation.
Terminal shorthand used below:

```bash
conda activate ai    # GPU/CUDA ML workstation environment (torch, fastapi, opencv, ...)
```

Activate it before every backend or ML command. The `base` environment is
deliberately torch-free and cannot run the API or training.

---

## 0. Quick start

```bash
conda activate ai
cd /home/kisuzoid/Kislay/Repo/Coding/college/Capstone1

# env template -> local .env (already present on this machine)
cp .env.example .env   # then edit: MODEL_PATH, GROQ_MODEL, GROQ_AUTO_INSPECT_API_KEY

# 1) Backend (port 8000)
uvicorn apps.api.main:app --reload --port 8000
# 2) Frontend (port 3000) — second terminal
cd apps/web && npm run dev
```

Open:

- `http://localhost:3000/` — scroll-driven cinematic intro
- `http://localhost:3000/demo` — the full inspection journey
- `http://localhost:8000/health` — backend health
- `http://localhost:8000/docs` — OpenAPI docs

---

## 1. Prerequisites (already installed on this machine)

| Tool | Where / notes |
|---|---|
| `ai` conda env | CUDA torch 2.5.1+cu121, fastapi, uvicorn, langgraph, langchain-groq, opencv, pillow |
| Node.js | v22.22.2 via nvm (frontend build) |
| CarDD dataset | `datasets/CarDD_COCO` (git-ignored) |
| Demo checkpoint | `ml/experiments/cardd_hybrid_ce/best_checkpoint.pt` (git-ignored, trained 2026-09-21; retrain if absent — see section 6) |
| System Chrome | used by Playwright (`channel: "chrome"`, no browser download) |

### `.env` — required keys

| Key | Purpose |
|---|---|
| `MODEL_PATH` | path to the checkpoint, e.g. `ml/experiments/cardd_hybrid_ce/best_checkpoint.pt` |
| `MODEL_VERSION` | e.g. `cardd_hybrid_ce` |
| `GROQ_MODEL` | assistant model name for LangChain ChatGroq (default `openai/gpt-oss-20b`) |
| `GROQ_AUTO_INSPECT_API_KEY` | assistant chat via LangChain ChatGroq; if empty, `build_assistant` wires the offline `StubAssistant` (no network) |
| `CORS_ORIGINS` | default `["http://localhost:3000"]` — needs no edit for the demo frontend |

All keys are documented in `.env.example`. Never commit `.env`.

---

## 2. Backend (FastAPI, port 8000)

Run in the `ai` env, from the repo root:

```bash
conda activate ai
uvicorn apps.api.main:app --reload --port 8000
```

- `--reload` is optional (dev convenience).
- Storage/session data is written under `storage/` and consented samples under
  `data/training/` (both git-ignored).
- Supabase/Postgres are **not** used today; the API uses stdlib SQLite at
  `storage/app.db` (see `DATABASE_URL` in `.env.example`).

Health check:

```bash
curl http://localhost:8000/health
# {"status":"ok","service":"autoinspect-api","environment":"development","version":"0.1.0"}
```

### API flow (photo-first)

The backend is deliberately small and follows ADR 0011 — no questionnaire, no
repair/cost fields anywhere:

```bash
# 1) create a session
curl -X POST http://localhost:8000/inspection/session

# 2) attach a photo
curl -X POST http://localhost:8000/inspection/<session_id>/upload \
  -F "file=@damage.jpg"

# 3) analyse it — quality gate then segmentation
curl -X POST http://localhost:8000/inspection/<session_id>/analyze
#   status=OK            -> inspection evidence + assistant explanation
#   status=QUALITY_FAILED-> 200 with retake guidance, no mask

# 4) optional consent (GRANTED | DECLINED)
curl -X POST http://localhost:8000/inspection/<session_id>/consent \
  -H "Content-Type: application/json" -d '{"decision":"DECLINED"}'

# 5) follow-up questions grounded in the stored evidence
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id":"<session_id>","message":"how bad is the scratch?"}'
```

---

## 3. Frontend (Next.js, port 3000)

```bash
cd apps/web
npm install          # once, if node_modules is missing
npm run dev
```

- API base URL defaults to `http://localhost:8000` (`NEXT_PUBLIC_API_URL`);
  set it in `apps/web/.env.local` if the backend runs elsewhere.
- The cinematic intro serves image frames from
  `apps/web/public/videos` — a symlink that must resolve to the repo-root
  `public/` directory (present on this clone; required on fresh clones).
- Frontend gates:

```bash
npm run lint && npm run typecheck && npm run build
```

---

## 4. End-to-end browser tests (Playwright)

```bash
cd apps/web
npx playwright test
```

`playwright.config.ts` boots both servers automatically (backend on `:8000`
from the `ai` env with the Groq key blanked — hermetic, offline `StubAssistant`;
`next start` on `:3000`). The backend is **not** silently reused, so a stale or
live server can never be tested by accident. Real-engine journeys run when the
checkpoint is present, otherwise they skip by design.

To deliberately run the suite against an already-running backend (e.g. the
fixed dev API on `:8000`), or against a different launcher:

```bash
REUSE_BACKEND=1 npx playwright test                       # target a running API
BACKEND_CMD="<launcher>" BACKEND_URL="<base>/health" npx playwright test
```

---

## 5. Backend / Python quality gates (in `ai`)

```bash
conda activate ai
cd /home/kisuzoid/Kislay/Repo/Coding/college/Capstone1

uv run ruff check apps/ ml/ tests/ conftest.py
uv run ruff format --check apps/ ml/ tests/ conftest.py
python -m mypy apps/ ml/ tests/
python -m pytest tests/
```

Order per CLAUDE.md: format → lint → type check → tests. ~123 tests; marked
integration/slow tests skip when the dataset or checkpoint is absent.

---

## 6. ML research track (optional, in `ai`)

```bash
conda activate ai

# Adapter/dataset machinery smoke check
python ml/training/smoke_test.py --data-root datasets/CarDD_COCO

# Evaluate an existing run (full splits + montages under ml/experiments/<run>/)
python ml/evaluation/evaluate_run.py \
  --data-root datasets/CarDD_COCO \
  --run-dir ml/experiments/cardd_hybrid_ce

# Train the hybrid (default; ADR 0010) on the RTX 3050 (~4 GB VRAM; batch 2 fits)
python ml/training/train.py \
  --data-root datasets/CarDD_COCO \
  --label cardd_hybrid_ce \
  --epochs 5 \
  --batch-size 2
# or pass --model cardd_unet for the plain U-Net baseline arm.
# The resulting best_checkpoint.pt carries a `model_arch` key and the engine
# dispatches on it; the demo default reads ml/experiments/cardd_hybrid_ce/.
```

The real-engine browser journeys and
`test_full_journey_happy_path_with_real_engine` skip (not fail) until
`ml/experiments/cardd_hybrid_ce/best_checkpoint.pt` has actually been trained
and its inference verified. As of 2026-09-21 the hybrid is trained (val mIoU
0.0504 / test 0.0586) and those journeys run and pass.

Training/inference artefacts (checkpoints, run records, `registry.json`) stay
git-ignored under `ml/experiments/`; only experiment IDs are referenced from
committed docs.

---

## 7. CI parity (without GitHub)

The same gates CI runs locally:

1. Backend gates (section 5).
2. Frontend gates: `cd apps/web && npm run lint -- --max-warnings=0 && npm run typecheck && npm run build`.
3. Playwright E2E (section 4) with `BACKEND_CMD` pointing at a CPU venv if you
   want to avoid the conda launcher.

GPU training never runs in CI.

---

## 8. Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `ModuleNotFoundError: torch / fastapi` | shell is not in `ai` — run `conda activate ai` |
| API `500`, `MODEL_UNAVAILABLE` on `/analyze` | `MODEL_PATH` unset or checkpoint missing — set `.env`, confirm `ml/experiments/cardd_hybrid_ce/best_checkpoint.pt` exists |
| API `500`, `INFERENCE_FAILED` on `/analyze` | model loaded but the forward pass failed — see backend logs for the real traceback |
| API `503`, `LLM_UNAVAILABLE` on `/chat` | `GROQ_AUTO_INSPECT_API_KEY` set but the ChatGroq call failed — check the key and `GROQ_MODEL`. The 2026-09-21 incident was a `404 model_not_found` for the old default `llama-3.3-70b-versatile` on this key; the code default is now `openai/gpt-oss-20b`. Clear the key to fall back to the offline `StubAssistant` |
| Playwright: API port in use | a manual backend occupies the port — stop it, or run with `REUSE_BACKEND=1`/`BACKEND_CMD` overrides |
| Frontend cannot reach API | backend not running on `:8000`, or `NEXT_PUBLIC_API_URL` / `CORS_ORIGINS` mismatch |
| Intro shows no frames | `apps/web/public/videos` symlink broken — recreate it to the repo-root `public/` |
| Playwright: browser not found | needs system Google Chrome on `PATH` (`channel: "chrome"`) |

---

## 9. Intent and honesty constraints

- The API returns an **AI inspection / decision support**, never a repair action,
  a repair-cost estimate, or a workshop quotation. Those are out of scope
  (ADR 0011) and no cost/quote field exists in any API response, state, or UI
  string.
- The overlay is always the model's **predicted** mask; area ratios are
  image-denominator (normalized), never cm². Segmentations flagged
  `low_confidence` are presented as preliminary, not verified damage extent.
- The demo hybrid was underfit (val mIoU ≈ 0.05 — MEASURED 2026-09-21); the
  full A1-vs-A3 write-up and the RQ2 metric are still pending before any
  stronger quality claim. Low-confidence honesty is by design, not a bug.
- With no `GROQ_AUTO_INSPECT_API_KEY` the assistant is a deterministic offline
  `StubAssistant` — a stand-in, never a live model.
- Never commit `.env`, datasets, checkpoints, or `storage/` / `data/` content.