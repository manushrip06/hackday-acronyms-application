# Agent instructions — Acronym Atlas

You are working in the **hackday-acronyms-application** monorepo.

## Read first (required)

1. **[docs/PLAN.md](docs/PLAN.md)** — master plan, scope, ownership, phases, demo, day-of timeline  
2. **[docs/architecture.md](docs/architecture.md)** — `Term` / `CandidateTerm` contracts and merge rules  
3. **[CONTRIBUTING.md](CONTRIBUTING.md)** — branching and folder ownership  

Doc index: [docs/README.md](docs/README.md)

## Ownership (do not thrash other areas)

| Area | Owner folder |
|------|----------------|
| Integrations / docs / Teams | `docs/`, `teams/`, root |
| Dictionary API | `apps/api/` |
| NLP / AI fine-tuning | `apps/nlp/` |
| Web UI | `apps/web/` |

Prefer small PRs into one owned area. Agree on shapes in `docs/architecture.md` before cross-cutting changes.

## Stack

- `apps/api` — FastAPI + SQLite; `X-Role: lead|member` hackday auth  
- `apps/nlp` — extractors + heuristic/LLM definitions; `POST /nlp/extract`  
- `apps/web` — Next.js upload / review / dictionary / lookup  
- `teams/` — sideloadable personal tab (no AppSource required)

## Do / don’t

- **Do** keep P0 scope from PLAN.md; cut list is intentional for hackday  
- **Do** preserve merge rules: never wipe approved terms on re-upload  
- **Do** fine-tune NLP via fixtures/tests under `apps/nlp/`  
- **Don’t** commit secrets (use `.env.example`)  
- **Don’t** require AppSource for Teams demo — sideload or web fallback  

## Local run

See [README.md](README.md). Typical ports: web `3000`, API `8000`, NLP `8001`.
