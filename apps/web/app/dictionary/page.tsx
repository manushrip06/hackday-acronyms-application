"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import { apiFetch, type Term } from "@/lib/api";
import { useRole } from "@/lib/role";

export default function DictionaryPage() {
  const { role, user } = useRole();
  const [q, setQ] = useState("");
  const [terms, setTerms] = useState<Term[]>([]);
  const [term, setTerm] = useState("");
  const [definition, setDefinition] = useState("");
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setError("");
    try {
      const path = q.trim() ? `/terms?q=${encodeURIComponent(q.trim())}` : "/terms";
      const data = await apiFetch<Term[]>(path, { role, user });
      setTerms(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }, [q, role, user]);

  useEffect(() => {
    void load();
  }, [load]);

  async function onSuggest(e: FormEvent) {
    e.preventDefault();
    setMsg("");
    setError("");
    try {
      await apiFetch<Term>("/terms", {
        method: "POST",
        role,
        user,
        body: JSON.stringify({ term, definition, aliases: [], kind: "other" }),
      });
      setMsg(`Suggested “${term}” — waiting for lead approval.`);
      setTerm("");
      setDefinition("");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }

  return (
    <>
      <h1>Dictionary</h1>
      <p className="lede">Browse approved terms. Anyone can suggest new jargon; only leads can edit.</p>

      <div className="panel">
        <div className="row">
          <input
            placeholder="Search…"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            style={{ maxWidth: 320 }}
          />
          <button className="secondary" type="button" onClick={() => void load()}>
            Search
          </button>
        </div>
        {error && <p className="msg error">{error}</p>}
        <table style={{ marginTop: "1rem" }}>
          <thead>
            <tr>
              <th>Term</th>
              <th>Definition</th>
            </tr>
          </thead>
          <tbody>
            {terms.map((t) => (
              <tr key={t.id}>
                <td>
                  <strong>{t.term}</strong>
                </td>
                <td>{t.definition}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <form className="panel" onSubmit={onSuggest}>
        <h2>Suggest a term</h2>
        <label htmlFor="term">Term</label>
        <input id="term" value={term} onChange={(e) => setTerm(e.target.value)} required />
        <div style={{ height: "0.75rem" }} />
        <label htmlFor="def">Definition</label>
        <textarea id="def" value={definition} onChange={(e) => setDefinition(e.target.value)} required />
        <div className="row" style={{ marginTop: "1rem" }}>
          <button className="primary" type="submit">
            Submit suggestion
          </button>
        </div>
        {msg && <p className="msg">{msg}</p>}
      </form>
    </>
  );
}
