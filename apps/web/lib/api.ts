export type Role = "lead" | "member";

export type Term = {
  id: string;
  team_id: string;
  term: string;
  definition: string;
  aliases: string[];
  status: string;
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
};

export type UploadResult = {
  document_id: string;
  filename: string;
  candidates_found: number;
  pending_created: number;
  pending_updated: number;
  conflicts: number;
  approved_unchanged: number;
};

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export function getApiUrl() {
  return API_URL;
}

export async function apiFetch<T>(
  path: string,
  opts: {
    method?: string;
    role: Role;
    user?: string;
    body?: BodyInit | null;
    headers?: Record<string, string>;
  }
): Promise<T> {
  const headers: Record<string, string> = {
    "X-Role": opts.role,
    "X-User": opts.user || opts.role,
    ...(opts.headers || {}),
  };
  if (opts.body && !(opts.body instanceof FormData)) {
    headers["Content-Type"] = headers["Content-Type"] || "application/json";
  }
  const res = await fetch(`${API_URL}${path}`, {
    method: opts.method || "GET",
    headers,
    body: opts.body,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}
