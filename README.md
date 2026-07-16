# Acronym Atlas (hackday)

Team jargon dictionary: upload docs → extract acronyms/terms → AI draft definitions → lead review → clickable lookup (web + sideloadable Teams personal tab).

Repo: [manushrip06/hackday-acronyms-application](https://github.com/manushrip06/hackday-acronyms-application)

## Shared plan (everyone + agents)

**Read this first so the team stays aligned:**

| Doc | What it is |
|-----|------------|
| **[docs/PLAN.md](docs/PLAN.md)** | Master plan — product, ownership, MVP scope, build phases, demo, day-of timeline |
| [docs/README.md](docs/README.md) | Index of all docs |
| [AGENTS.md](AGENTS.md) | Instructions for AI coding agents |
| [docs/architecture.md](docs/architecture.md) | API/NLP contracts |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Branches, PRs, folder ownership |

## Quick start (local)

```bash
# 1) Env
cp .env.example .env

# 2) NLP service (terminal A)
cd apps/nlp
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001

# 3) API (terminal B)
cd apps/api
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
mkdir -p data/uploads
uvicorn app.main:app --reload --port 8000

# 4) Web (terminal C)
cd apps/web
npm install
npm run dev
```

Open http://localhost:3000

Optional seed reset: `./scripts/seed-demo.sh`

Or with Docker: `docker compose up --build` (set `OPENAI_API_KEY` in `.env` if desired).

## Roles (hackday auth)

Headers: `X-Role: lead|member` and optional `X-User: name`. The web UI toggles Lead/Member in the header.

| Role | Can do |
|------|--------|
| member | Suggest terms, search, lookup |
| lead | Upload, review/approve/edit/delete |

## Team of 4 ownership

See [CONTRIBUTING.md](CONTRIBUTING.md). Folder owners:

- **A** — `/docs`, `/teams`, root
- **B** — `/apps/api`
- **C** — `/apps/nlp`
- **D** — `/apps/web`

## Collaboration on GitHub

- Labels: `area:*`, `priority:p0`, `good-first`
- Milestone: **Hackday MVP** (+ issues #1–#8)
- Branch: `feature/<person>-<thing>` → PR → squash merge
- **Branch protection:** repo owner should enable “Require pull request before merging” + 1 review on `main` (needs Admin; collaborators with Write cannot set this)

Add teammates: Settings → Collaborators → Write. Keep Admin for the owner.

## Fine-tuning NLP

Work in `apps/nlp/`:

- Extractors: `app/extractors.py`
- Definitions: `app/define.py` (heuristics without API key; OpenAI/Azure when configured)
- Fixtures: `fixtures/` + `pytest` in `tests/`

API falls back to mock candidates if NLP is down (`USE_MOCK_NLP=true` forces mock).

## Teams (no store approval)

See [teams/README.md](teams/README.md) — HTTPS tunnel + sideload zip. Demo fallback = full-screen web UI.

## Demo

[docs/demo-script.md](docs/demo-script.md) · sample docs in [docs/sample-docs/](docs/sample-docs/)

## Full documentation

See **[docs/PLAN.md](docs/PLAN.md)** and the [docs index](docs/README.md).
