# Demo Script (3–4 minutes)

## Backup recording checklist

- [ ] Seed DB once (`./scripts/seed-demo.sh`) and verify Lookup highlights PIR / GTM / BAU
- [ ] Record 60–90s Loom/QuickTime of happy path **before** the live demo
- [ ] Keep `docs/sample-docs/team-wiki.md` and offline screenshots if Wi‑Fi dies
- [ ] Have OpenAI key ready **or** rely on heuristic definitions (no key = still works)
- [ ] Confirm who drives: Person A owns the happy path

## Live story

### 1. Problem (20s)

> New hire in Teams chat sees: **“Can we schedule a PIR after the GTM for the BAU runbook?”**  
> They don’t know the jargon. Every team invents its own acronyms.

### 2. Lead uploads docs (45s)

1. Switch role to **Lead** in the web app.
2. Open **Upload** → upload `docs/sample-docs/team-wiki.md`.
3. Show **Review** queue filling with AI/heuristic definitions.
4. Edit one wrong definition → **Approve**; approve the rest (or Approve all).

### 3. New hire lookup (45s)

1. Switch role to **Member**.
2. Open **Lookup**, paste: `PIR after the GTM for the BAU runbook`.
3. Click **PIR** / **GTM** / **BAU** → definition popovers.
4. Toggle “Jargon assist” off/on briefly.

### 4. Member suggests a term (30s)

1. Dictionary → **Suggest term**: e.g. `SWAG` = “Scientific Wild-Ass Guess (team planning estimate)”.
2. Switch to Lead → Review → Approve.

### 5. Re-upload (30s)

1. Lead uploads `docs/sample-docs/team-wiki-v2.md` (adds a new acronym).
2. Show only **new** pending terms; approved terms untouched.

### 6. Teams path (20s)

- Prefer: open the **sideloaded personal tab** (same UI).
- Fallback: full-screen web app + show `teams/manifest.json` — “same surface as a Teams tab; no AppSource needed for hackday.”

## Closing line

> Documentation in → team dictionary out → click any jargon in chat or docs to learn it. Leads stay in control; everyone else can look up and suggest.
