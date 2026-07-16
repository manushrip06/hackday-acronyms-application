# Architecture

Shared contracts for the Hackday Acronyms monorepo.

## Roles

| Role | Can do |
|------|--------|
| `member` | Suggest terms, search dictionary, use lookup |
| `lead` | Everything members can + upload docs, approve/edit/reject, delete |

Hackday auth: headers `X-Role: lead|member` and optional `X-User: <name>`.

## Term

```json
{
  "id": "uuid",
  "team_id": "default",
  "term": "PIR",
  "definition": "Post-Incident Review — meeting after a production incident.",
  "aliases": ["post-incident review"],
  "status": "pending|approved|rejected",
  "source": "upload|suggest|seed",
  "kind": "acronym|camelcase|entity|noun_phrase|other",
  "confidence": 0.0,
  "context": "… surrounding snippet …",
  "conflict_note": null,
  "created_by": "lead",
  "updated_by": "lead",
  "last_seen_at": "ISO-8601",
  "created_at": "ISO-8601",
  "updated_at": "ISO-8601"
}
```

## CandidateTerm (NLP → API)

```json
{
  "term": "PIR",
  "kind": "acronym",
  "definition": "Post-Incident Review …",
  "confidence": 0.82,
  "context": "… after the PIR we updated …",
  "aliases": []
}
```

## Pipeline

```
upload → text extract → NLP /nlp/extract → merge into pending Terms → lead review → approved dictionary → lookup UI / Teams tab
```

### Merge rules (re-upload)

1. New term → insert `pending`.
2. Exact match of existing `approved` → bump `last_seen_at`; if AI definition differs meaningfully, set `conflict_note` for lead (do **not** overwrite approved definition).
3. Exact match of existing `pending` → update definition/confidence/context from latest extraction.
4. Never wipe approved terms on re-upload.

## Services

| Path | Role |
|------|------|
| `apps/api` | FastAPI + SQLite: dictionary, upload, review, calls NLP |
| `apps/nlp` | Extractors + optional OpenAI definitions; `POST /nlp/extract` |
| `apps/web` | Next.js admin + lookup UI |
| `teams/` | Sideloadable personal tab manifest |

## NLP extractors (P0)

- Acronyms: `\b[A-Z]{2,6}\b` and `Term (ACR)` patterns
- CamelCase / PascalCase tokens
- Capitalized multi-word spans
- Repeated noun phrases (frequency ≥ N)

Fine-tune in `apps/nlp/fixtures/` without blocking UI (API can mock NLP).
