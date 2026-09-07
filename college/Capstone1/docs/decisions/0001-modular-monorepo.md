# ADR 0001 — Modular monorepo instead of microservices

- **Status:** Accepted
- **Date:** 2026-09-07

## Context

AutoInspect-X has three parts that must evolve together: a React frontend, a
FastAPI backend, and an ML training and inference stack. It is a capstone
project built by a small team, with reproducibility and a clear demo as primary
goals.

## Decision

Use a single repository organised as a modular monorepo: `apps/web`, `apps/api`,
`ml/`, `packages/shared`, with enforced dependency direction and no direct
cross-boundary imports.

## Rationale

- One commit hash describes the whole system, which matters for reproducing an
  experiment alongside the code that served it.
- Contracts between frontend, backend, and inference change frequently early on.
  Coordinating those changes across repositories costs more than it protects.
- Microservices would add deployment and network complexity with no scaling
  requirement to justify it.
- Module boundaries with a stated dependency direction give most of the
  separation benefit without the operational cost.

## Consequences

- Boundaries are a convention, so they need enforcement in review; an import
  that crosses a boundary is a defect, not a shortcut.
- CI must handle both Python and Node toolchains in one repository.
- Extracting a component later remains possible because the boundaries are
  explicit from the start.
- Directories are created only when a task justifies them; empty scaffolding
  invites speculative code.
