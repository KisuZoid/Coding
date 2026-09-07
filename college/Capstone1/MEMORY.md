# MEMORY.md — AutoInspect-X

Running memory of what changed in this repository and why. Append a new entry
after every update, newest at the bottom. `TASKS.md` records *what was asked*;
this file records *what the project now believes to be true*.

Entry format:

```
## YYYY-MM-DD — <title>
**Change:** what changed
**Reasoning:** why it was done this way
**Current logic / state after the change:** the state a future session inherits
**Open questions:** anything unresolved
```

---

## 2026-09-07 — Repository bootstrap

**Change:**
Created the foundation of the repository: session protocol (`init.md`), agent
and tooling rules (`CLAUDE.md`, `AGENTS.md`), continuity files (`MEMORY.md`,
`TASKS.md`, `LOGIC.md`), project documentation (`README.md`, `CONTRIBUTING.md`,
`SECURITY.md`), architecture and research documentation under `docs/`, four
ADRs, Python tooling configuration, an environment template, ignore rules, and a
minimal CI workflow. Initialised Git.

**Reasoning:**
The bootstrap brief requires an architecture-first foundation with no product
functionality. Directories with no justified content were deliberately not
created, because empty scaffolding invites speculative code in later sessions.

**Current logic / state after the change:**

- The repository contains documentation and configuration only. There is no
  application code, ML code, database, or frontend.
- The research document `AutoInspect-X_Research_Report_Corrected.md` is **not**
  present. Everything in `docs/research/` is derived from the bootstrap brief
  alone and is marked as provisional until the research document arrives.
- Verified environment: Node v22.22.2, Python 3.13.12, uv 0.11.11, Docker
  present. Vercel CLI and n8n CLI are not installed.
- MCP servers: `playwright` configured; `github` configured but failing to
  connect ("Incompatible auth server: does not support dynamic client
  registration"); claude.ai Supabase connector available; Vercel plugin server
  available. **No n8n MCP server is configured.**
- Supabase: the connected account holds one project only, "Physios Plus CRM V3"
  (`nykalxhmbupsarhicrtd`), which belongs to a different product. AutoInspect-X
  has no Supabase project. Writing to that ref from this repository is
  prohibited.
- Automation: none exists. `LOGIC.md` documents the intended location and the
  contract that any future workflow must satisfy.

**Open questions:**

1. Where is the research document, and does it change the pipeline framing used
   in this bootstrap?
2. Which segmentation dataset will be used, and under which licence?
3. What is the real source of repair-cost labels? Until that is answered, cost
   values must be treated as SYNTHETIC LABEL, never as REAL GROUND TRUTH.
4. Does this project need a database at all, and if so, Supabase or Postgres?
5. Is any n8n automation actually planned, or was the mention exploratory?
