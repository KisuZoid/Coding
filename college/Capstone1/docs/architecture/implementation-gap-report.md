# Implementation Gap Report — AutoInspect-X Product Build

> Status: **superseded (2026-09-08).** This was the Phase A audit that scoped the
> phased build. Phases A–R are now complete; see `docs/architecture/overview.md`
> for the implemented system. This report is retained as a historical record of
> the baseline audit and its recommended order.
>
> Original banner:
> **audit deliverable (Phase A), 2026-09-08.** Repository-wide audit of the
> current research baseline against the complete-product brief. No application
> code was written to produce this report. Findings below are the basis for the
> phased build (phases A–R of the brief).

---

## 1. What already works

- **CarDD data layer:** `ml/datasets/cardd_adapter.py` — typed COCO reader (splits,
  categories, images, polygon rasterization); `cardd_audit.py` +
  `ml/datasets/reports/cardd_audit.json` (counts, imbalance, duplicate check).
  Class mapping confirmed: `1=dent, 2=scratch, 3=crack, 4=glass shatter,
  5=lamp broken, 6=tire flat`.
- **Training pipeline:** `ml/training/train.py` (CE over argmax target, ADR 0008),
  `loss.py`, `cardd_dataset.py` (lazy, split-scoped, augmentable, 512×512),
  `cardd_unet.py` (CarddUNet, base 64, 7 channels).
- **Evaluation harness:** `ml/evaluation/metrics.py` (IoU/Dice/precision/recall),
  `small_damage.py` (train-p25 criterion ≈ 3,014 px @512), `evaluate_run.py`
  (full-split summary + montages), `ml/analysis/error_analysis.py` (case
  selection + overlays + `CLASS_COLORS`).
- **Experiment provenance:** `ml/experiments/registry.json` + per-run
  `run_record.json`; `cardd_baseline_ce` is the current inference candidate
  (base 64, CE, best val mIoU 0.0475 — **underfit baseline, not production**).
- **Quality gates:** ruff/mypy(strict)/pytest (22 tests) green; dataset-gated
  tests skip cleanly without data.
- **Runtime:** all backend/MLL packages already installed in the `ai` conda env:
  fastapi 0.136, uvicorn 0.46, pydantic + settings, python-multipart, httpx,
  **langgraph 1.1.9, groq 0.37, langchain**, torch 2.5.1+cu121, opencv, numpy,
  pillow, onnxruntime. Node v22.22.2 + npm 10.9.7 for the frontend.
- **Kinematic assets:** `public/1.mp4` … `4.mp4` exist (see §Video inspection).

## 2. What is missing

- No `apps/web` or `apps/api`; no FastAPI server, no LangGraph graph, no Groq
  integration, no frontend of any kind.
- No `ml/inference/` module (**ADR 0003 requires it**; API must not import
  `ml/training`).
- No image-quality validation stage (blur/dark/glare/framing/visibility).
- No damage-feature extraction service (instances, confidence, area ratio,
  position, shape — only evaluation-harness code exists, not a production path).
- No repair/replace interface; no cost service (honest `DATA_UNAVAILABLE` state).
- No typed `InspectionContext` (incident/vehicle/location/vision/provenance).
- No storage layer, session lifecycle, cleanup service, or training-data consent
  workflow.
- No scroll-driven cinematic player, no chat UI, no result/explanation screens.
- No Playwright E2E config; `.github/workflows/ci.yml` does not exist despite
  being claimed in docs.

## 3. What can be reused

- `CarddUNet` + `best_checkpoint.pt` (`cardd_baseline_ce`) = the real inference
  engine (load pattern proven in `evaluate_run.py` / `error_analysis.py`:
  `torch.load(..., weights_only=False)` → `Model(..., base=ckpt["base"])`
  → `load_state_dict(ckpt["model_state"])`).
- `CLASS_COLORS`, `overlay`/`blend`/`edge_of`/`montage` from
  `ml/evaluation/evaluate_run.py` + `ml/analysis/error_analysis.py` for the
  segmentation overlay endpoint (to be moved under `ml/inference`).
- Class names + split policy from `cardd_adapter.py`; area-ratio rule from
  ADR 0005 (image-denominator only; never cm²).
- `cross_entropy_loss` / `aggregate_targets` semantics document the decode the
  inference service must mirror (argmax over 7 channels, background = class 0).
- `.env.example` already declares `API_URL`, `GROQ_AUTO_INSPECT_API_KEY`,
  `MODEL_PATH`, `MODEL_VERSION`, DB/Supabase placeholders.
- Research conclusions (ADRs 0005/0008/0009, cost-readiness report) define the
  honest output contract the product must expose.

## 4. What must be added

1. `ml/inference/` — model loader + preprocessing (mirror training: bilinear to
   512², /255, CHW), argmax decode, softmax confidence, connected-component
   instance extraction, per-instance features (class, confidence, pixel area,
   `damage_area_ratio_image`, bbox, centroid), JSON-serialisable result, and an
   overlay-image generator. Config via `MODEL_PATH`/`MODEL_VERSION` env.
2. `apps/api/` — FastAPI + routers (`/chat`, `/inspection/*`,
   `/inspection/image`, `/inspection/validate-image`, `/inspection/analyze`,
   `/inspection/consent`, `GET/DELETE /inspection/{id}`); thin routers over
   application services; domain pydantic models; storage interfaces.
3. Image-quality validator (blur/dark/glare/framing/visibility → VALID /
   TOO_BLURRY / TOO_DARK / EXCESSIVE_GLARE / WRONG_ANGLE /
   DAMAGE_NOT_VISIBLE / INSUFFICIENT_CONTEXT).
4. LangGraph workflow (nodes = orchestration only, no ML inside) + Groq
   conversational service (backend-only key).
5. Repair-action interface (REPAIR / REPLACE / MANUAL_REVIEW) backed by a
   clearly-labelled "preliminary demonstration rule", swappable for the learned
   model later.
6. Cost interface returning `cost_status=DATA_UNAVAILABLE` with the mandated
   explanation; P10/P50/P90 structure reserved; synthetic demo values only
   behind an explicit `ALLOW_SYNTHETIC_ESTIMATE` flag, always labelled
   "DEMO / SYNTHETIC ESTIMATE — NOT A REAL QUOTE".
7. Storage layer (`ImageStore`, `SessionStore`, `TrainingSampleStore`,
   `ConsentStore`) + ephemeral session cleanup + optional training consent.
8. `apps/web/` — Next.js frontend (cinematic intro, chat, context summary,
   photo guidance, upload/camera, validation UX, analysis stages, results,
   explanation, consent, completion); responsive mobile/tablet/desktop.
9. Playwright E2E tests + CI workflow (`ci.yml`).
10. `docs/architecture/overview.md` rewrite to reflect the real implementation.

## 5. What should NOT be added

- **No second segmentation model / no "silent replacement"** of the current U-Net
  as inference engine; future better checkpoints drop into the same interface.
- **No cost fabrication, no fake masks/confidences/severity** — the model is the
  only source of vision evidence; severity is intermediate and may be reported
  as "not currently reliable".
- **No auto-retraining from user uploads** — collected data waits for dataset
  review, label validation, versioning, explicit offline training.
- **No part-normalized area** (`damage_pixels/part_pixels`) — banned by ADR 0005
  until a part-mask source is adopted via a new ADR; never label area as cm².
- **No writes to the Physios Plus CRM V3 Supabase project**; no new Supabase
  project without explicit user approval (bootstrap/CLAUDE.md rules).
- **No LLM pretending to be the vision model**, no hidden-damage diagnostics,
  no insurance secrets/passwords collection, no full-conversation storage.
- **No giant file/module** — each phase lands as a coherent, tested module.

## 6. Dependencies required

- **Python runtime (net-new: ~none).** The `ai` env already provides fastapi,
  uvicorn, pydantic(+settings), python-multipart, langgraph, groq, langchain
  core, torch, opencv, numpy, pillow. The backend runs in the `ai` env
  (same env as ML, CUDA available). App deps will be declared in a new
  `apps/api/pyproject.toml` for the lockfile/documentation; root stays
  `package=false`.
- **Frontend (net-new node packages in `apps/web/`):** next, react, react-dom,
  typescript, tailwindcss (+ `@playwright/test` dev). No GSAP unless the
  cinematic interaction genuinely needs it; HTML5 video `currentTime` driving
  is the baseline approach.
- **No new MCP servers, no new conda env, no n8n.**

## 7. Storage decision

- **Now:** local, zero-provisioning storage, safely behind interfaces:
  - Session temp images/masks/intermediates → `storage/sessions/<session_id>/`
    (filesystem), wiped on session close/expiry.
  - Ephemeral session + consent metadata → **SQLite** via stdlib `sqlite3`
    (no new dependency), schema: `InspectionSession`, `ConsentRecord`,
    `TrainingSample` (with provenance), plus image-asset records.
  - Consented training samples → `data/training/<dataset_version>/` (files),
    referenced from SQLite; separate from ephemeral sessions.
- **Later:** swap `ImageStore`/`SessionStore`/`TrainingSampleStore` for
  S3/Postgres/Supabase without touching domain logic. No Supabase project is
  created now.

## 8. Frontend architecture

- `apps/web` — Next.js App Router, React 19, TypeScript strict, Tailwind.
- Single journey, not unrelated pages: cinematic landing → agent chat → context
  summary → photo guidance → upload/camera → validation → analysis stages →
  results (+overlay) → explanation → optional consent → completion.
- Scroll-driven cinematic: one pinned section over the four clips; scroll
  progress (0→1) maps to total timeline 0→30.42 s (video 1: 0–10 s, video 2:
  10–18 s, video 3: 18–22.4 s, video 4: 22.4–30.4 s), seeking each clip's
  `currentTime`; text overlays tied to progress; smooth hand-off to the agent
  ("Talk to AutoInspect-X" / "Start Inspection").
- Results clarity: four labelled blocks (WHAT YOU TOLD US / WHAT THE MODEL FOUND
  / WHAT WE ESTIMATE / WHAT WE RECOMMEND); low-confidence banner; cost
  unavailable state; bottom-sheet modals on mobile (rejection UX).
- Performance: lazy-mount cinematic, `preload="metadata"`, code-split views,
  responsive from ~375 px up; reduced-motion fallback.

## 9. Backend architecture

`apps/api` with the mandated layering (router → application service → domain →
infrastructure):

- `api/` — thin FastAPI routers (chat, inspection CRUD, image upload,
  validate-image, analyze, consent, feedback).
- `agent/` — LangGraph StateGraph (START → understand_request →
  collect_incident → collect_damage_location → collect_vehicle →
  collect_repair_location → collect_insurance_if_needed → check_context_ready →
  photo_guidance → receive_photo → validate_image [FAIL loops to photo_guidance]
  → damage_analysis → feature_extraction → compare_user_vs_model →
  downstream_prediction → cost_availability → result_validation →
  final_explanation → training_consent → session_cleanup → END) + Groq
  conversation/extraction/explanation service (key server-side only).
- `inspection/` — typed `InspectionContext` + provenance (USER / MODEL / DERIVED
  / INFERRED / SYSTEM), user-vs-model comparison (AGREEMENT / PARTIAL_AGREEMENT
  / DISAGREEMENT), photo-guidance templates per reported panel.
- `vision/` — image-quality validation + overlay/feature presentation (calls
  `ml/inference` only).
- `cost/` — `CostEstimator` interface; real path = quantile model later; current
  path returns `DATA_UNAVAILABLE` (+ optional behind-flag synthetic demo).
- `repair/` — `RepairEstimator` interface with labelled demonstration rule.
- `storage/` — interface implementations (fs + sqlite); cleanup service.
- `shared/` — pydantic schemas/contracts shared with the frontend.

## 10. ML integration plan

- New `ml/inference/` module (respects ADR 0003 — API never imports
  `ml/training`). `DamageInference` loads the checkpoint once at startup,
  validates inputs, returns typed structured results + always a confidence.
- Preprocessing mirrors training exactly (bilinear 512², /255, CHW) so
  reported numbers stay comparable to the research evaluation.
- Per-instance extraction via connected components over the argmax damage map;
  features: damage_type (CarDD class name), confidence (region softmax
  probability), mask pixel count, `damage_area_ratio_image`, bbox, centroid,
  instance count, `needs_review` when confidence is low.
- Visualization: overlay PNG/JPEG endpoint reusing the existing overlay helpers
  (moved under `ml/inference`), `CLASS_COLORS` kept as single source.
- The underfit `cardd_baseline_ce` artifact is used **for demonstration** with
  confidence + low-confidence mode; a future stronger checkpoint replaces it via
  the same `MODEL_PATH`-resolved loader — no app rewrite.

## 11. Security risks

- **Groq key exposure:** key lives in `.env` only; used server-side; never sent
  to the browser; never logged; CORS strictly limited to the frontend origin.
- **Uploaded images:** validate type/size at the boundary, strip EXIF (location
  data) before storage, never log raw image bytes or absolute paths; respond
  with opaque asset/session ids, not file paths.
- **Model artefacts:** checkpoint paths from `MODEL_PATH` env, never hard-coded;
  checkpoints already git-ignored (`ml/experiments/`).
- **No secrets in logs or error responses;** pydantic validation at every
  boundary; no credentials anywhere in the demo deployment.

## 12. Privacy risks

- Images may contain number plates/faces → EXIF strip, short retention, deletion
  at session end; persistence only under explicit consent.
- No exact residential addresses; repair-city-level context only.
- Conversation is used to drive the inspection and generate explanations; only a
  minimal, consented `TrainingSample` (image + labels + context + provenance +
  consent + dataset version) may persist — never full chat history, insurance
  details, or personal identifiers.
- Ephemeral vs persistent lifetimes kept distinct so session cleanup can never
  delete a consented training record; consent is always optional and labelled
  so.

## 13. Research risks

- **Underfit baseline** (val mIoU 0.0475) must never be presented as production
  performance; product uses confidence + low-confidence warnings + honest
  explanations. This is demonstration-grade inference, documented as such.
- **No cost labels** → the cost head always returns `DATA_UNAVAILABLE` (or
  labelled synthetic demo); nothing may pass as a real quote.
- **No part masks** → area stays image-normalized; never cm²; no severity
  overclaim.
- `ml/experiments/registry.json` lacks a STATUS/superseded field (superseded
  runs are documented only in ADR prose) — service should ignore superseded
  runs; add a field when the registry is next touched.
- The conversational/product layer must not distort the research methodology
  (two-track rule): research = segmentation → features → fusion → downstream
  comparison; product = cinematic UI → conversation → photo flow → inference →
  results → consent.

## 14. Recommended implementation order

Follow the brief's phases A–R, each ending with tests + lint + type check +
review + TASKS.md/MEMORY.md updates:

1. **A — Repository reconciliation** *(this report)*.
2. **B — Backend foundation**: `apps/api` package, settings, pydantic contracts,
   health endpoint, storage interfaces; run in `ai` env.
3. **C — Image/storage service**: upload validation, EXIF strip, session-scoped
   fs storage, sqlite session/consent/training tables, cleanup service.
4. **D — Real segmentation inference API**: `ml/inference/` + `/inspection/analyze`
   returning typed instances/features/overlay + confidence.
5. **E — Image-quality validation**: validator service + `validate-image` +
   rejection contract.
6. **F — Inspection context schema**: typed context + provenance + user-vs-model
   comparison.
7. **G — LangGraph workflow**: the mandated graph with loops; pydantic state.
8. **H — Groq integration**: conversation, extraction, explanation, photo
   instructions (server-side).
9. **I — Repair-action interface**: labelled demonstration rule.
10. **J — Cost interface**: `DATA_UNAVAILABLE` path (+ optional flagged demo).
11. **K — Training-data consent/storage**: consent flow + training sample write.
12. **L — Frontend foundation**: Next.js scaffold, design system, responsive
    shell.
13. **M — Chat + inspection UI**: agent chat, context summary, photo guidance,
    upload/camera, validation UX.
14. **N — Result visualization**: overlay + result screen + explanation + consent.
15. **O — Cinematic video experience**: scroll-driven sequence over the four
    clips (mapping in §8).
16. **P — Full end-to-end integration**.
17. **Q — Playwright testing**: desktop/tablet/mobile E2E incl. poor image,
    retry, disagreement, low confidence, unavailable cost, Groq/API failure.
18. **R — Cleanup + documentation**: dead-code sweep, `overview.md` rewrite,
    this report superseded, `ci.yml` created, TASKS/MEMORY/LOGIC updates.

---

## Appendix — Video inspection evidence (2026-09-08)

Frames could not be read semantically by the coding agent (no image input
support for this model). Programmatic inspection of the actual files:

| Asset | Container | Frames | Duration (s) | 24 fps | Resolution | Signature |
|---|---|---|---|---|---|---|
| `public/1.mp4` | h264 | 240 | 10.00 | yes | 1920×1080 | continuous shot; neutral/daylight (mean lum ≈ 112, sat ≈ 27) |
| `public/2.mp4` | h264 | 192 | 8.00 | yes | 1920×1080 | darker (lum ≈ 86), one scene cut, sat ≈ 47 |
| `public/3.mp4` | h264 | 106 | 4.42 | yes | 1280×720 | bright/even (lum ≈ 122, sat ≈ 38), continuous |
| `public/4.mp4` | h264 | 192 | 8.00 | yes | 1920×1080 | darkest + highest contrast (lum p5 54 → p95 121), most saturated (≈ 76) |

Total timeline ≈ **30.4 s**. Proposed phase boundaries for the scroll map:
video 1 spans 0–10 s, video 2 10–18 s, video 3 18–22.4 s, video 4 22.4–30.4 s.
**Open item:** exact narrative copy per clip is to be confirmed against visual
content once a vision-capable reviewer (user or a later capability) inspects the
clips, or against the user's intended storyline — do not hard-code narrative
copy that presumes unseen content.