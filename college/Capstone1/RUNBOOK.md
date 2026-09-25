# RUNBOOK.md — AutoInspect-X

Operational guide for the photo-first API, model catalogue, frontend, and
research commands.

## 0. Environment

Use the `ai` conda environment for Python, model loading, training, and
Playwright's default backend launcher. The base environment is intentionally
torch-free.

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate ai
cd /home/kisuzoid/Kislay/Repo/Coding/college/Capstone1
```

Create or update local configuration without committing it:

```bash
cp .env.example .env
```

Set `MODEL_ID=final60_hybrid_seed42` for the default catalogue model. Leave the
Groq key empty to use the deterministic offline assistant. `MODEL_PATH` and
`MODEL_VERSION` are retained only for deliberate legacy/custom-checkpoint use.

## 1. Start the product

Backend:

```bash
uvicorn apps.api.main:app --reload --port 8000
```

Frontend, in a second terminal:

```bash
cd apps/web
npm install
npm run dev
```

Useful URLs:

- `http://localhost:3000/` — cinematic introduction.
- `http://localhost:3000/demo` — photo-first inspection.
- `http://localhost:8000/health` — API health.
- `http://localhost:8000/docs` — OpenAPI.

The demo selector calls `GET /models`, creates a session with the selected
`model_id`, and locks the selection after analysis. The default is
`final60_hybrid_seed42`; `final100_hybrid_seed42` is labelled exploratory and
is not evidence of a completed 100-epoch run.

## 2. Model catalogue

| ID | Family | Seed | Status | Best val foreground mIoU |
|---|---|---:|---|---:|
| `final60_baseline_seed42` | ResNet34 U-Net | 42 | CONTROLLED | 0.6676585078 |
| `final60_baseline_seed1337` | ResNet34 U-Net | 1337 | CONTROLLED | 0.6681153178 |
| `final60_hybrid_seed42` | CNN–Transformer hybrid | 42 | CONTROLLED; default | 0.6701672077 |
| `final60_hybrid_seed1337` | CNN–Transformer hybrid | 1337 | CONTROLLED | 0.6731674075 |
| `final100_hybrid_seed42` | CNN–Transformer hybrid | 42 | EXPLORATORY | 0.6715497971 |

`final100_hybrid_seed42` has `record_status =
PARTIAL_RECONSTRUCTED_FROM_CHECKPOINTS`; its complete epoch history and
termination reason are unavailable. The four controlled entries are the
current two-seed comparison, not a completed three-seed study.

## 3. API flow

Create a session and optionally select a catalogue model:

```bash
curl -X POST http://localhost:8000/inspection/session \
  -H "Content-Type: application/json" \
  -d '{"model_id":"final60_hybrid_seed42"}'
```

Change the selection before analysis:

```bash
curl -X PATCH http://localhost:8000/inspection/<session_id>/model \
  -H "Content-Type: application/json" \
  -d '{"model_id":"final60_baseline_seed1337"}'
```

Upload and analyze:

```bash
curl -X POST http://localhost:8000/inspection/<session_id>/upload \
  -F "file=@damage.jpg"
curl -X POST http://localhost:8000/inspection/<session_id>/analyze
```

`analyze` returns `OK` with predicted evidence or `QUALITY_FAILED` with retake
guidance and no mask. Optional consent and follow-up chat are then available:

```bash
curl -X POST http://localhost:8000/inspection/<session_id>/consent \
  -H "Content-Type: application/json" \
  -d '{"decision":"DECLINED"}'
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id":"<session_id>","message":"what does the overlay show?"}'
```

Unknown model IDs return `MODEL_NOT_FOUND`. Selection after analysis returns
`MODEL_SELECTION_LOCKED`.

## 4. Static and browser gates

Backend:

```bash
conda activate ai
ruff check apps/ ml/ tests/ conftest.py
ruff format --check apps/ ml/ tests/ conftest.py
python -m mypy apps/ ml/ tests/
python -m pytest tests/
```

Frontend:

```bash
cd apps/web
npm run lint -- --max-warnings=0
npm run typecheck
npm run build
```

Playwright starts its own key-blanked backend by default:

```bash
cd apps/web
npx playwright test
```

Set `REUSE_BACKEND=1` only when deliberately targeting an already-running API.
Real-engine browser tests skip when the local checkpoint is absent.

## 5. Evaluate an active run

```bash
conda activate ai
python ml/evaluation/evaluate_run.py \
  --data-root datasets/CarDD_COCO \
  --run-dir ml/experiments/final60_hybrid_seed42 \
  --num-examples 8
```

Evaluation writes `evaluation_summary.json` and qualitative outputs under the
run directory. Do not interpret a missing evaluation output as a zero result.

## 6. Reproduce a controlled run

The training CLI records configuration and appends a registry entry. Use a
new label or archive an existing run before repeating an experiment; never
silently overwrite a measured run.

Baseline, seed 42:

```bash
python ml/training/train.py \
  --data-root datasets/CarDD_COCO \
  --label final60_baseline_seed42 \
  --model baseline \
  --epochs 60 \
  --batch-size 4 \
  --grad-accum 1 \
  --seed 42
```

Hybrid, seed 42:

```bash
python ml/training/train.py \
  --data-root datasets/CarDD_COCO \
  --label final60_hybrid_seed42 \
  --model hybrid \
  --epochs 60 \
  --batch-size 4 \
  --grad-accum 1 \
  --seed 42
```

Repeat with `--seed 1337` and labels `final60_baseline_seed1337` and
`final60_hybrid_seed1337` for the second controlled seed. The existing
hybrid-seed-1337 run record includes its resume metadata; preserve that
provenance when interpreting its best checkpoint.

The exploratory continuation is documented separately and must not be presented
as a matched comparison:

```bash
python ml/training/train.py \
  --data-root datasets/CarDD_COCO \
  --label final100_hybrid_seed42 \
  --model hybrid \
  --epochs 100 \
  --batch-size 4 \
  --grad-accum 1 \
  --seed 42 \
  --resume ml/experiments/final60_hybrid_seed42/best_checkpoint.pt
```

The current `final100_hybrid_seed42` record was reconstructed from available
checkpoints and periodic metadata; it has `completed: false`.

## 7. Troubleshooting

| Symptom | Action |
|---|---|
| `ModuleNotFoundError: torch` or `fastapi` | Activate the `ai` environment. |
| `MODEL_UNAVAILABLE` | Check `MODEL_ID`, then confirm the selected run's `best_checkpoint.pt` exists. |
| `MODEL_NOT_FOUND` | Use one of the five IDs returned by `GET /models`. |
| `MODEL_SELECTION_LOCKED` | Create a new session; a model cannot change after evidence exists. |
| `LLM_UNAVAILABLE` during chat | Check `GROQ_AUTO_INSPECT_API_KEY` and `GROQ_MODEL`, or clear the key for the offline stub. |
| Frontend cannot reach API | Check backend port 8000, `NEXT_PUBLIC_API_URL`, and `CORS_ORIGINS`. |
| Missing cinematic frames | Check the `apps/web/public/videos` symlink and `public/` frame directories. |
| Playwright cannot find Chrome | Use the configured system Chrome channel or install it before rerunning. |

## 8. Evidence and storage rules

- Predicted masks and confidence are MODEL PREDICTION outputs.
- Image-relative area is a DERIVED FEATURE, never cm².
- Consent is optional and does not convert predictions into ground truth.
- Repair cost/action, hidden damage, and physical area are not product outputs.
- Active experiment directories retain only the best checkpoint and run record.
- Pilot and legacy artifacts belong under `archive/experiments/`.
- Never commit `.env`, datasets, `*.pt`, `*.pth`, `storage/`, or
  `ml/experiments/`.

## 9. Current verification state

The model catalogue/API focused tests, Ruff, mypy, and frontend lint,
typecheck, and build passed during the current change. Full pytest, Playwright,
documentation compilation, and deliverable regeneration remain tracked in
`TASKS.md`. The `public/4/` textual OCR audit is complete; direct visual
interpretation was unavailable in the current tool environment.
