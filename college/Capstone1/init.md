# init.md — AutoInspect-X Session Bootstrap Protocol

> **Read this file at the start of every Claude Code session in this repository.**
> It exists so a new session can orient itself without guessing, and without
> confusing this project with any other project on this machine.

---

## 0. Session start checklist

Run these steps in order, before answering anything substantive.

1. Read `init.md` (this file).
2. Read `CLAUDE.md` — tooling, MCP, and engineering rules.
3. Read `AGENTS.md` — agent behaviour rules for this repository.
4. Read `MEMORY.md` — what changed in previous sessions and why.
5. Read `TASKS.md` — numbered task history and current state.
6. Read `LOGIC.md` — workflow/automation logic, if any exists yet.
7. Read the research document (see section 2). It is the source of truth for
   all research-facing claims.
8. Run `git status` and `git log --oneline -10` to see the real current state.

Do not start implementing until steps 1–8 are done.

---

## 1. Project identity (do not confuse with other repos)

- **Name:** AutoInspect-X
- **Path:** `/home/kisuzoid/Kislay/Repo/Coding/college/Capstone1`
- **Type:** Academic capstone research project + supporting product prototype.
- **Research title:** *AutoInspect-X: Multimodal Deep Learning for Vehicle Damage
  Segmentation and Uncertainty-Aware Repair Cost Estimation*
- **Research question:** Can segmentation-derived damage representations,
  combined with vehicle metadata, improve repair-cost estimation and
  repair-action prediction compared with vision-only and simple-fusion baselines?

This repository is **not** related to any other project in
`/home/kisuzoid/Kislay/Repo/`. In particular it is **not** related to
Physios Plus CRM, AppSynergies client work, or any portfolio repository.

---

## 2. Research document

Expected filename in repository root:

```
AutoInspect-X_Research_Report_Corrected.md
```

**Current status: NOT PRESENT in the repository.**

Rules:

- The research document is the baseline for terminology, literature, datasets,
  equations, research questions, hypotheses, metrics, and limitations.
- Read it before changing any research-facing architecture or documentation.
- Never fabricate research results, datasets, citations, market figures, or
  ground truth.
- Never silently strengthen a scientific claim beyond what the document supports.
- Record any material correction as an ADR in `docs/decisions/`.
- If the file is still missing, say so explicitly instead of inventing content,
  and keep research documents in `docs/research/` marked as placeholders.

---

## 3. Supabase — which project belongs to this repository

**Answer today: none.**

Verified via the Supabase MCP connector on 2026-09-07. The connected Supabase
account contains exactly one project:

| Project name | Ref | Region | Belongs to AutoInspect-X? |
|---|---|---|---|
| Physios Plus CRM V3 | `nykalxhmbupsarhicrtd` | ap-southeast-2 | **No** |

**Rule: never read from or write to `nykalxhmbupsarhicrtd` from this repository.**
That project belongs to a different product. Writing to it would corrupt
unrelated production data.

### How to determine the correct Supabase project in a future session

1. Check for an environment file in this repository:
   ```bash
   ls -a | grep -E '^\.env'
   cat .env 2>/dev/null | grep -i supabase
   ```
2. The project ref is the subdomain of `SUPABASE_URL`:
   `https://<project-ref>.supabase.co` → `<project-ref>`.
3. Confirm that ref against `mcp__claude_ai_Supabase__list_projects`.
4. If the ref in `.env` is not in the list, stop and ask the user. Do not guess.
5. If no `.env` exists, this repository has no database yet. Do not create a
   Supabase project without explicit approval — provisioning costs money.

`.env` is git-ignored. Only `.env.example` is tracked.

---

## 4. n8n / automation — how to check

**Current status: no n8n integration exists in this repository.**

Verified on 2026-09-07:

- No n8n MCP server is configured. Configured MCP servers are `github`
  (currently failing to connect), `playwright`, the claude.ai Supabase
  connector, and the Vercel plugin server.
- The `n8n` CLI is not installed on this machine.
- No workflow JSON, no `automation/` directory, no webhook handler exists here.

### How to check for n8n in a future session

```bash
# 1. Is an n8n MCP server configured?
python3 -c "import json,os;d=json.load(open(os.path.expanduser('~/.claude.json')));print(list(d.get('mcpServers',{}).keys()))"
claude mcp list 2>/dev/null

# 2. Is n8n running locally?
docker ps --format '{{.Names}}\t{{.Image}}' | grep -i n8n
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:5678/healthz

# 3. Does this repository contain automation assets?
ls automation/ 2>/dev/null
grep -rIl 'n8n' --include='*.json' --include='*.ts' --include='*.py' . 2>/dev/null
```

### Where automation will live, once it exists

| Concern | Location |
|---|---|
| Exported n8n workflow JSON | `automation/n8n/` |
| Workflow logic, triggers, data contracts | `LOGIC.md` |
| Webhook endpoints consumed by n8n | `apps/api/` (documented in `LOGIC.md`) |
| Credentials | environment variables only, never committed |

If the user asks about "the automation" and none of the above exists, say so
rather than describing a workflow that was never built.

---

## 5. Current repository state

As of the bootstrap session (2026-09-07):

- Documentation and engineering rules only.
- No application code, no ML code, no database, no frontend, no CI-tested build.
- `apps/`, `ml/`, `packages/`, `tests/` are intentionally **not** created yet.

See `TASKS.md` for the authoritative task log and `MEMORY.md` for the
change history.

---

## 6. Hard rules that survive every session

1. Read before writing. Search the repository before adding any new file.
2. Smallest coherent change that solves the task. No unrelated refactors.
3. No speculative abstraction. No frameworks for hypothetical requirements.
4. No fake production logic — no mock outputs, hard-coded predictions, or empty
   endpoints presented as working code.
5. Never commit secrets, datasets, or model checkpoints.
6. Keep these label categories distinct and never blur them: REAL GROUND TRUTH,
   WEAK LABEL, SYNTHETIC LABEL, DERIVED FEATURE, MODEL PREDICTION, ASSUMPTION.
7. Update `TASKS.md` and `MEMORY.md` at the end of every working session.
