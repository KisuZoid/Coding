# AutoInspect-X

**Multimodal Deep Learning for Vehicle Damage Segmentation and Uncertainty-Aware
Repair Cost Estimation**

> **Status: implemented prototype.** Segmentation research baseline, FastAPI
> backend, and Next.js frontend exist and run locally. See `RUNBOOK.md` for how
> to run everything.

---

## Research question

Can segmentation-derived damage representations, combined with vehicle metadata,
improve repair-cost estimation and repair-action prediction compared with
vision-only and simple-fusion baselines?

## Intended pipeline

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
Repair action prediction   +   Repair cost distribution (lower / median / upper)
      ↓
Explainable report
```

Hidden-damage risk prediction is optional and out of scope unless real
ground-truth labels become available.

## Scope boundary

AutoInspect-X produces an **AI estimate and decision support**. It does not
produce a final professional workshop quotation, and the interface must always
make that distinction visible.

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

## Missing input

The research document `AutoInspect-X_Research_Report_Corrected.md` is not yet in
this repository. It is the source of truth for terminology, literature,
datasets, equations, research questions, hypotheses, metrics, and limitations.
Everything in `docs/research/` is provisional until it arrives.

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
