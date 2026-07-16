# Contributing

**Shared plan (required reading):** [docs/PLAN.md](docs/PLAN.md) · doc index: [docs/README.md](docs/README.md) · agents: [AGENTS.md](AGENTS.md)

## Branching

- Protect `main`: merge via PR only (1 review required when branch protection is enabled).
- Branch naming: `feature/<person>-<thing>` (e.g. `feature/alex-upload-api`).
- Prefer **squash merge**.
- Tag demo-ready commits: `demo-v1`.

## Ownership (minimize merge conflicts)

| Person | Owns | Primary folders |
|--------|------|-----------------|
| **A — Lead / PM+Integrations** | Repo hygiene, README, env, Teams, demo, deploy | `/docs`, `/teams`, root config |
| **B — Backend / Dictionary** | Auth roles, CRUD, upload, storage, APIs | `/apps/api` |
| **C — NLP / AI** | Extraction, prompts, definitions, fixtures | `/apps/nlp` (+ NLP routes only) |
| **D — Frontend** | Upload, review, lookup UI | `/apps/web` |

Rule: **one owner per folder**. Others open PRs into that area only with the owner’s review.

## Workflow

1. Pick an issue from the **Hackday MVP** milestone / Project board.
2. Create a short-lived branch from `main`.
3. Keep PRs small and focused on one area.
4. Agree on shared JSON shapes in [`docs/architecture.md`](docs/architecture.md) before deep UI/NLP work.
5. Mock NLP with fixtures until `/nlp/extract` is ready.

## Auth (hackday)

Use header `X-Role: lead` or `X-Role: member` (and optional `X-User: yourname`). Documented in `.env.example` and README. Swap for real auth later.

## Secrets

Never commit API keys. Copy `.env.example` → `.env`.
