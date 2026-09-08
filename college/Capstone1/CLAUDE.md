# CLAUDE.md — AutoInspect-X

Operating manual for Claude Code in this repository. `init.md` is the session
start protocol; this file is the reference for tooling, MCP servers, and
engineering rules.

**Precedence:** user instruction → `CLAUDE.md` / `AGENTS.md` → skill suggestions
→ default model behaviour.

---

## 1. Project summary

AutoInspect-X estimates vehicle repair cost and repair action from photographs,
using damage segmentation combined with vehicle metadata.

```
Vehicle image(s)
      ↓
Damage / vehicle-part segmentation
      ↓
Damage representation (type, area ratio, location, part, confidence, geometry)
      +  Vehicle metadata (make, model, year/age, region)
      ↓
Multimodal fusion
      ↓
  ┌──────────────────────────┬─────────────────────────────┐
  │ Repair action prediction │ Cost distribution / range   │
  │ repair / replace /       │ lower / median / upper      │
  │ manual inspection        │ quantile estimates          │
  └──────────────────────────┴─────────────────────────────┘
      ↓
Explainable report
```

Hidden-damage risk prediction is **optional**, and only in scope if real
ground-truth labels become available.

---

## 2. Machine environment (verified 2026-09-07)

| Tool | Status |
|---|---|
| Node.js | v22.22.2 (via nvm) |
| npm | present |
| Python (default shell) | 3.13.12 (miniconda3) |
| uv | 0.11.11 — preferred Python dependency manager |
| Docker | present |
| Vercel CLI | **not installed** (`npm i -g vercel` if deployment work starts) |
| n8n CLI | **not installed** |

### AI workstation environment (use this for ML work)

The **`ai`** conda environment is the ML workstation and the only environment with a
CUDA-enabled PyTorch. Use it for anything that needs `torch`, model training, or
GPU inference. Do **not** install CUDA/torch runtimes into the base environment.

```bash
source ~/miniconda3/etc/profile.d/conda.sh && conda activate ai
```

Verified in `ai` (2026-09-07):

| Package | Version |
|---|---|
| Python | 3.12.13 |
| torch | 2.5.1+cu121 |
| torchvision | 0.20.1+cu121 |
| transformers | 5.9.0 |
| opencv-python / opencv-contrib-python | 4.13.0.92 |
| numpy | 2.4.3 |
| scikit-learn | 1.8.0 |
| pandas | 2.3.3 |
| matplotlib | 3.10.9 |
| mlflow | 3.11.1 |

Hardware: **NVIDIA GeForce RTX 3050 Laptop GPU, ~4 GB VRAM, CUDA 13.0 driver**.
Treat this as constrained GPU hardware (brief §29): lazy loading, small batches,
mixed precision, gradient accumulation.

**Not present in `ai`:** `ultralytics`, `pycocotools`, `albumentations`. Add
`pycocotools` (needed to read COCO segmentation) as a dev/research dependency when
the dataset-audit work begins; justify any other add.

---

## 3. MCP servers

| Server | Status | Use for |
|---|---|---|
| `claude_ai_Supabase` | Connected | Database inspection and migrations — **see the warning below** |
| `playwright` | Configured | Browser verification once a UI exists |
| Vercel plugin server | Configured | Deployment work only, and only when deployment is actually relevant |
| `github` | **Failing to connect** — "Incompatible auth server: does not support dynamic client registration" | GitHub issues/PRs. Report the failure to the user rather than assuming no access exists. |
| n8n | **Not configured** | See `init.md` §4 for how to check and where automation would live |

### Supabase warning

The connected account has exactly one project, **Physios Plus CRM V3**
(`nykalxhmbupsarhicrtd`), which belongs to a **different** product.
AutoInspect-X currently has **no** Supabase project.

- Never run `execute_sql`, `apply_migration`, or any write tool against
  `nykalxhmbupsarhicrtd` from this repository.
- Resolve the correct project from `.env` (`SUPABASE_URL` subdomain), never from
  memory or from the project list ordering.
- Do not create a Supabase project without explicit user approval — it costs money.

---

## 4. Skills and plugins — routing rules

Use the smallest relevant tool set. Do not invoke overlapping skills for the
same task.

| Task | Skill / tool |
|---|---|
| Frontend visual work | `ui-ux-pro-max` |
| Browser verification of a running UI | Playwright MCP |
| GitHub issues / PRs | GitHub MCP (currently unavailable) |
| Current library or API documentation | Context7 |
| Deployment / Vercel | Vercel skills and MCP — only when deploying |
| Engineering workflow, TDD, debugging | `superpowers` |
| Generic reusable skill | `everything-claude-code`, only when clearly relevant |

Rules:

- Verify any ambiguous package name against its exact repository before installing.
- Do not install additional MCP servers without a concrete need.
- `AGENTS.md` and this file take precedence over generic skill suggestions.

---

## 5. Repository layout

Present today:

```
AutoInspect-X/
├── docs/
│   ├── architecture/    # System architecture
│   ├── research/        # Research scope, problem definition, experiment principles
│   ├── ml/              # ML engineering guidelines
│   └── decisions/       # ADRs
├── ml/
│   ├── datasets/        # CarDD audit + typed data adapter (cardd_adapter.py, cardd_audit.py)
│   │   └── reports/     # cardd_audit.json (experiment documentation)
│   ├── models/          # CarddUNet (smoke U-Net, ADR 0006)
│   ├── training/        # PyTorch dataset adapter, smoke test, smoke + real trainers, shared loss
│   ├── evaluation/      # segment. metric harness (metrics.py: IoU/Dice, Phase 4)
│   └── experiments/     # run records + checkpoints + registry.json (git-ignored)
├── tests/               # pytest: adapter, dataset, metrics tests (dataset-gated skips)
├── src/public/          # Demo videos 1-4.mp4 (staged; content unverified)
├── init.md              # Session bootstrap protocol
├── CLAUDE.md            # This file
├── AGENTS.md            # Agent rules
├── MEMORY.md            # Change log with reasoning
├── TASKS.md             # Numbered task history
├── LOGIC.md             # Workflow / automation logic
├── RUNBOOK.md           # Everything on this machine: how to run it locally
├── README.md
├── CONTRIBUTING.md
├── SECURITY.md
├── pyproject.toml       # Python tooling configuration
├── .env.example
├── .editorconfig
└── .gitignore
```

Dataset roots (`datasets/`) are git-ignored; commit `ml/datasets/reports/`
documentation instead. Key ADRs: 0003 (training/inference separation),
0004 (ground-truth labelling policy), 0005 (CarDD has no part masks →
only image-denominator area ratio is derivable), 0006 (segmentation framework =
raw PyTorch small U-Net).

Planned, and deliberately **not** created yet — create each only when a task
justifies it:

```
apps/web/      apps/api/
ml/inference/
packages/shared/
scripts/       automation/n8n/
```

### Dependency direction

```
web       → api contracts
api       → domain → application → infrastructure
ml        → datasets / models / evaluation
web      ↛ ml internals
api      ↛ training internals
training ↛ frontend
```

No direct cross-boundary imports.

---

## 6. Backend rules

- Python, FastAPI, Pydantic, pytest, Ruff, mypy, uv.
- Layering: router → application service → domain → infrastructure.
- Business logic never lives in route handlers.
- Do not create ORM models, repositories, services, or endpoints before their
  responsibilities are known.
- Future logical modules: inspections, vehicles, damages, estimates, reports, models.

## 7. Frontend rules

- React with TypeScript, strict typing, accessible components, responsive layouts.
- Every view handles loading, error, and empty states explicitly.
- Consistent typography, spacing, and a restrained professional visual system.
- Avoid: random gradients, heavy glassmorphism, decorative cards with no semantic
  purpose, emoji as interface decoration, mixed icon libraries, over-animation,
  generic template-dashboard aesthetics.
- The interface must clearly separate an **AI estimate / decision support** from a
  **final professional workshop quotation**.
- Planned screens: Dashboard, Inspection Upload, Inspection Result, Damage
  Visualization, Repair Estimate, Inspection History, Report, Settings.

## 8. ML rules

- Training and inference stay separate. Training code never lives in the API app.
- Never hard-code dataset paths, checkpoint paths, model versions, secrets, or
  experiment parameters. Use configuration and environment variables.
- Detail lives in `docs/ml/ml-engineering-guidelines.md`.

---

## 9. Quality gates

```
format → lint → type check → unit tests → integration / E2E when applicable
```

- GPU training never runs in CI.
- ML evaluation belongs to explicit experiment runs, not the normal test suite.
- Browser tests use Playwright, once a UI exists.

## 10. Secrets and data

- Real secrets never enter the repository. Update `.env.example` instead.
- Never commit datasets, trained checkpoints, API keys, tokens, passwords,
  certificates, or cloud credentials.

## 11. AI coding discipline

1. **Inspect before coding.** Search for existing files, helpers, hooks,
   services, components, models, schemas, and utilities before adding new ones.
2. **Minimal change.** Smallest coherent change; no unrelated refactors.
3. **No speculative abstraction.** No interfaces, factories, generic wrappers, or
   registries for hypothetical requirements.
4. **No dead code.** Remove unused imports, variables, functions, components,
   commented-out production code, unreachable logic, and obsolete configuration
   before finishing.
5. **No fake production logic.** No `TODO`/`pass`/mock output/hard-coded
   prediction/fake database response presented as real behaviour, unless the task
   explicitly asks for scaffolding and it is clearly marked as such.
6. **Dependency discipline.** Before adding a dependency, check existing
   dependencies and the standard library, decide whether it is a runtime,
   development, or research dependency, and document why it was added.

## 12. Session bookkeeping

At the end of every working session, update:

- `TASKS.md` — the numbered task, the user's prompt, and the steps completed.
- `MEMORY.md` — what changed, and the reasoning behind it.
- `LOGIC.md` — only when workflow or automation logic changed.
