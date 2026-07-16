/**
 * Shared Term / CandidateTerm TypeScript shapes (mirror of docs/architecture.md).
 */
export type TermStatus = "pending" | "approved" | "rejected";

export interface CandidateTerm {
  term: string;
  kind: string;
  definition: string;
  confidence: number;
  context: string;
  aliases: string[];
}

export interface Term {
  id: string;
  team_id: string;
  term: string;
  definition: string;
  aliases: string[];
  status: TermStatus | string;
  source: string;
  kind: string;
  confidence: number;
  context: string;
  conflict_note?: string | null;
  created_by: string;
  updated_by: string;
  last_seen_at: string;
  created_at: string;
  updated_at: string;
}
