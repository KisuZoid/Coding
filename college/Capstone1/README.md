# AutoInspect-X

**Photo-first vehicle damage segmentation — turn one photograph into a
pixel-level damage mask and an honest, conversational inspection.**

> **Status: implemented prototype.** FastAPI backend, segmentation engine
> (`CarddHybrid` / `CarddUNet`), LangChain-based chat assistant, and Next.js
> frontend exist and run locally. See `RUNBOOK.md` for how to run everything.

---

## Research question

With the photo-first scope (ADR 0011) AutoInspect-X answers one honest question:
**where is the damage, and how sure can we honestly be?**
Concretely, the research comparisons are:

- **RQ1 — segmentation quality:** does the CNN+Transformer hybrid
  (`CarddHybrid`, ADR 0010) beat the plain U-Net baseline (`CarddUNet`) on
  CarDD for mIoU, Dice, pixel accuracy, and the small-damage slice?
- **RQ2 — confidence honesty:** how honestly do the models label their own
  confidence?

`cardd_hybrid_ce` has been trained and its inference verified (val mIoU 0.0504 /
test 0.0586, MEASURED — see `AUTOINspectX_PROJECT_STATE.md`), but the full
head-to-head comparison and the RQ2 confidence-honesty metric remain open.

## Intended pipeline

```
Photo (attached in the chat composer)
      ↓
Capture-quality gate (blur / dark / glare / framing / visibility)
      ↓  on rejection → 200 QUALITY_FAILED + assistant retake guidance
Damage segmentation (CarddHybrid by default; legacy CarddUNet) — 7-channel argmax
      ↓
Evidence payload: classes, image-denominator area ratios, confidence,
      low-confidence flag, quality, model metadata + predicted-mask overlay
      ↓
Assistant chat (LangChain ChatGroq when a key is set; offline stub otherwise)
      ↓  optional consent
Follow-up questions
```

Hidden-damage risk prediction is optional and out of scope unless real
ground-truth labels become available.

## Scope boundary

AutoInspect-X produces an **AI inspection / decision support** from photographs.
It does not produce repair actions, repair-cost estimates, or a workshop
quotation — those are out of scope (ADR 0011). The overlay is always the model's
**predicted** mask, and area ratios are normalized (image-denominator), never cm².

## Features

- **Photo-first inspection** — create a session, upload a photo, run `analyze`
  (quality gate → segmentation → evidence), optionally consent, then ask
  follow-ups via `POST /chat`.
- **Capture-quality gate** — blur/dark/glare/low-contrast shots are rejected
  with a `200 QUALITY_FAILED` response and assistant retake guidance; no mask is
  produced for a rejected photo (ADR 0007).
- **Segmentation engine** — `CarddHybrid` (CNN + transformer bottleneck,
  ~3.2 M params) by default; the engine dispatches on the checkpoint's
  `model_arch` key so legacy `CarddUNet` checkpoints keep loading (ADR 0010).
- **Honest evidence** — predicted masks only; image-denominator area ratios;
  explicit low-confidence flags; no cost/repair/quote fields anywhere in the
  API or UI.
- **Chat assistant** — LangChain `ChatGroq`
  (`openai/gpt-oss-20b`, `GROQ_MODEL`) when `GROQ_AUTO_INSPECT_API_KEY` is
  set; a deterministic offline `StubAssistant` otherwise. If the live LLM fails
  while analyzing a photo, the structured segmentation result is still
  returned with `assistant_fallback=true` (the LLM is a non-blocking stage of
  `/analyze`).

---

## Repository map

| Path | Contents |
|---|---|
| `init.md` | Session start protocol — read this first |
| `CLAUDE.md` | Tooling, MCP servers, and engineering rules |
| `AGENTS.md` | Rules for AI coding agents |
| `MEMORY.md` | Change history with reasoning |
| `TASKS.md` | Numbered task log |
| `LOGIC.md` | Pipeline, workflow, and automation logic |
| `docs/architecture/` | System architecture |
| `docs/research/` | Problem definition, scope, experiment principles |
| `docs/ml/` | ML engineering guidelines |
| `docs/decisions/` | Architecture Decision Records |

## Research document

`AutoInspect-X_Research_Report_Corrected.md` is the source of truth for
terminology, literature, datasets, equations, research questions, hypotheses,
metrics, and limitations. `AUTOINspectX_PROJECT_STATE.md` records the current
project state. Read both before touching anything research-facing (see
`AGENTS.md`).

## Getting started

```bash
conda activate ai                                     # CUDA/ML workstation env
cp .env.example .env                                  # never commit .env
uvicorn apps.api.main:app --reload --port 8000        # backend
cd apps/web && npm run dev                            # frontend at :3000
```

Full runbook (backend, frontend, Playwright E2E, gates, ML track,
troubleshooting): `RUNBOOK.md`.

## Contributing

See `CONTRIBUTING.md`. Security policy: `SECURITY.md`.
