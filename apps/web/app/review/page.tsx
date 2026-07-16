"use client";

import { useCallback, useEffect, useState } from "react";
import { apiFetch, type Term } from "@/lib/api";
import { useRole } from "@/lib/role";
import { useTeam } from "@/lib/team";

export default function ReviewPage() {
  const { role, user } = useRole();
  const { teamId, activeTeam } = useTeam();
  const [items, setItems] = useState<Term[]>([]);
  const [error, setError] = useState("");
  const [edits, setEdits] = useState<Record<string, string>>({});

  const load = useCallback(async () => {
    setError("");
    if (role !== "lead") {
      setItems([]);
      setError("Switch to Lead to review pending terms.");
      return;
    }
    try {
      const data = await apiFetch<Term[]>("/review", { role, user, teamId });
      setItems(data);
      setEdits(Object.fromEntries(data.map((t) => [t.id, t.definition])));
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }, [role, user, teamId]);

  useEffect(() => {
    void load();
  }, [load]);

  async function save(term: Term) {
    await apiFetch<Term>(`/terms/${term.id}`, {
      method: "PATCH",
      role,
      user,
      teamId,
      body: JSON.stringify({ definition: edits[term.id] ?? term.definition }),
    });
  }

  async function approve(term: Term) {
    await save(term);
    await apiFetch(`/review/${term.id}/approve`, { method: "POST", role, user, teamId });
    await load();
  }

  async function reject(term: Term) {
    await apiFetch(`/review/${term.id}/reject`, { method: "POST", role, user, teamId });
    await load();
  }

  async function approveAll() {
    for (const term of items.filter((t) => t.status === "pending")) {
      await save(term);
      await apiFetch(`/review/${term.id}/approve`, { method: "POST", role, user, teamId });
    }
    await load();
  }

  return (
    <>
      <h1>Review queue</h1>
      <p className="lede">
        {activeTeam.name} — edit AI drafts, then approve or reject. Approved terms then show in
        Dictionary.
      </p>
      <div className="panel">
        <div className="row" style={{ marginBottom: "1rem" }}>
          <button className="secondary" type="button" onClick={() => void load()}>
            Refresh
          </button>
          <button className="primary" type="button" onClick={() => void approveAll()} disabled={!items.length}>
            Approve all pending
          </button>
        </div>
        {error && <p className="msg error">{error}</p>}
        {!error && !items.length && <p className="msg">No pending items.</p>}
        {!!items.length && (
          <table>
            <thead>
              <tr>
                <th>Term</th>
                <th>Definition</th>
                <th>Meta</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {items.map((t) => (
                <tr key={t.id}>
                  <td>
                    <strong>{t.term}</strong>
                    <div>
                      <span className={`badge ${t.status}`}>{t.status}</span>{" "}
                      <span className="badge">{t.kind}</span>
                    </div>
                  </td>
                  <td>
                    <textarea
                      value={edits[t.id] ?? ""}
                      onChange={(e) => setEdits((s) => ({ ...s, [t.id]: e.target.value }))}
                      style={{ minHeight: 90 }}
                    />
                    {t.conflict_note && (
                      <p className="msg error" style={{ marginTop: 6 }}>
                        {t.conflict_note}
                      </p>
                    )}
                  </td>
                  <td>
                    <div className="msg">conf {t.confidence.toFixed(2)}</div>
                    <div className="msg">{t.context}</div>
                  </td>
                  <td>
                    <div className="row">
                      <button className="primary" type="button" onClick={() => void approve(t)}>
                        Approve
                      </button>
                      <button className="danger" type="button" onClick={() => void reject(t)}>
                        Reject
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
}
