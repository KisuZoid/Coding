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
cp .env.example .env   # then edit: MODEL_PATH, GROQ_AUTO_INSPECT_API_KEY

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
| `ai` conda env | CUDA torch 2.5.1+cu121, fastapi, uvicorn, langgraph, groq, opencv, pillow |
| Node.js | v22.22.2 via nvm (frontend build) |
| CarDD dataset | `datasets/CarDD_COCO` (git-ignored) |
| Demo checkpoint | `ml/experiments/cardd_baseline_ce/best_checkpoint.pt` (git-ignored) |
| System Chrome | used by Playwright (`channel: "chrome"`, no browser download) |

### `.env` — required keys

| Key | Purpose |
|---|---|
| `MODEL_PATH` | path to the checkpoint, e.g. `ml/experiments/cardd_baseline_ce/best_checkpoint.pt` |
| `MODEL_VERSION` | e.g. `cardd_baseline_ce` |
| `GROQ_AUTO_INSPECT_API_KEY` | LLM extraction; the agent falls back to rule-based if empty/modern key absent |
| `ALLOW_SYNTHETIC_ESTIMATE` | keep `false`; synthetic cost is behind an explicit flag |
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
from the `ai` env, `next start` on `:3000`) and reuses already-running ones.
Uses the system Google Chrome (no browser download). Real-engine journeys run
when the checkpoint is present, otherwise they skip by design.

To point the config at a different backend launcher (used on CI):

```bash
BACKEND_CMD="<launcher>" npx playwright test
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
  --run-dir ml/experiments/cardd_baseline_ce

# Train a new baseline on the RTX 3050 (~4 GB VRAM; batch 2 fits)
python ml/training/train.py \
  --data-root datasets/CarDD_COCO \
  --label my_run \
  --epochs 5 \
  --batch-size 2
```

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
| API `500` on `/analyze` | `MODEL_PATH` unset or checkpoint missing — set `.env`, confirm `ml/experiments/cardd_baseline_ce/best_checkpoint.pt` exists |
| Frontend cannot reach API | backend not running on `:8000`, or `NEXT_PUBLIC_API_URL` / `CORS_ORIGINS` mismatch |
| Intro shows no frames | `apps/web/public/videos` symlink broken — recreate it to the repo-root `public/` |
| Playwright: browser not found | needs system Google Chrome on `PATH` (`channel: "chrome"`) |
| Port already in use | both servers were started manually while Playwright/config also started them — stop one, or reuse the running one |

---

## 9. Intent and honesty constraints

- The API returns an **AI estimate and decision support**, never a final
  workshop quotation. Cost is `DATA_UNAVAILABLE` unless
  `ALLOW_SYNTHETIC_ESTIMATE=true` and then always labelled
  `DEMO / SYNTHETIC ESTIMATE — NOT A REAL QUOTE`.
- The demo baseline is underfit (val mIoU ≈ 0.05); results usually carry
  `low_confidence=true`. That is honest, by design — not a bug.
- Never commit `.env`, datasets, checkpoints, or `storage/` / `data/` content.