# TASKS.md — AutoInspect-X

Numbered log of every task requested, the prompt behind it, and the steps
actually completed. Newest task at the bottom. Never delete an entry; append a
follow-up entry instead.

Entry format:

```
## Task N — <short title>
**Date:** YYYY-MM-DD
**Status:** Completed | In progress | Blocked | Abandoned
**Prompt (summary):** what the user asked for
**Steps completed:** what was actually done
**Files created / changed:** paths
**Not done, and why:** explicit exclusions
**Follow-up:** next recommended step
```

---

## Task 1 — Repository bootstrap: architecture, engineering rules, session memory files

**Date:** 2026-09-07
**Status:** Completed

**Prompt (summary):**
Supplied the "AutoInspect-X — Claude Code Project Bootstrap & Engineering Rules"
brief. Instructed to inspect the repository, read the research document,
compare the repository against the brief, and create only the necessary
bootstrap files and documentation — no ML model, database, production API,
dashboard, training pipeline, or cost-estimation engine. Additionally requested
four session-continuity files: `init.md` (session start protocol, including how
to check the n8n MCP, where automation lives, and which Supabase project belongs
to this repository), `CLAUDE.md` (MCP and tooling reference), `MEMORY.md`
(running memory of updates and logic), `TASKS.md` (this file), and `LOGIC.md`
(workflow and automation logic).

**Steps completed:**

1. Inspected the working directory: `/home/kisuzoid/Kislay/Repo/_/Capstone1` was
   completely empty and was not a Git repository.
2. Searched the parent tree for the research document
   `AutoInspect-X_Research_Report_Corrected.md` — not found anywhere under
   `/home/kisuzoid/Kislay`.
3. Verified the toolchain: Node v22.22.2, Python 3.13.12, uv 0.11.11, Docker
   present; Vercel CLI and n8n CLI absent.
4. Verified MCP configuration: `github` (connection failing) and `playwright`
   configured in `~/.claude.json`; claude.ai Supabase connector and Vercel plugin
   server available. No n8n MCP server configured.
5. Queried the Supabase connector: the account contains exactly one project,
   "Physios Plus CRM V3" (`nykalxhmbupsarhicrtd`), which belongs to a different
   product. Recorded an explicit rule never to write to it from this repository.
6. Initialised a Git repository.
7. Created the bootstrap documentation, engineering rules, session-continuity
   files, Python tooling configuration, environment template, ignore rules, and
   a minimal CI workflow.

**Files created:**

- `init.md`, `CLAUDE.md`, `AGENTS.md`, `MEMORY.md`, `TASKS.md`, `LOGIC.md`
- `README.md`, `CONTRIBUTING.md`, `SECURITY.md`
- `pyproject.toml`, `.env.example`, `.editorconfig`, `.gitignore`
- `docs/architecture/overview.md`
- `docs/research/problem-definition.md`, `docs/research/research-scope.md`,
  `docs/research/experiment-principles.md`
- `docs/ml/ml-engineering-guidelines.md`
- `docs/decisions/0001-modular-monorepo.md`,
  `docs/decisions/0002-python-tooling.md`,
  `docs/decisions/0003-separate-training-and-inference.md`,
  `docs/decisions/0004-ground-truth-labelling-policy.md`
- `.github/workflows/ci.yml`

**Not done, and why:**

- `apps/web/`, `apps/api/`, `ml/*`, `packages/shared/`, `scripts/`, `tests/` —
  the brief forbids implementing functionality during bootstrap, and empty
  directories carry no information.
- `package.json` and frontend tooling — no frontend code exists yet, so lint and
  type-check configuration for it would be unused configuration.
- Any Supabase schema or project — this repository has no database yet, and
  provisioning costs money.
- Any n8n workflow — no automation requirement has been specified yet.
- Research content in `docs/research/` is scoped from the bootstrap brief only
  and is explicitly marked as awaiting the research document.

**Follow-up:**

1. Add `AutoInspect-X_Research_Report_Corrected.md` to the repository root, then
   reconcile `docs/research/` against it.
2. Decide the segmentation dataset and record it as an ADR with source, licence,
   class mapping, and split policy.
