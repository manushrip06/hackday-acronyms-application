import type { Term } from "./api";

export function buildTermIndex(terms: Term[]): Map<string, Term> {
  const map = new Map<string, Term>();
  for (const t of terms.filter((x) => x.status === "approved")) {
    map.set(t.term.toLowerCase(), t);
    for (const alias of t.aliases ?? []) {
      const key = alias.trim().toLowerCase();
      if (key) map.set(key, t);
    }
  }
  return map;
}

export function findTerm(query: string, index: Map<string, Term>): Term | null {
  const key = query.trim().toLowerCase();
  if (!key) return null;
  return index.get(key) ?? null;
}

export function normalizeSelection(raw: string): string {
  const trimmed = raw.trim();
  if (!trimmed) return "";
  if (!trimmed.includes(" ")) {
    return trimmed.replace(/^[^A-Za-z0-9]+|[^A-Za-z0-9]+$/g, "");
  }
  return trimmed;
}