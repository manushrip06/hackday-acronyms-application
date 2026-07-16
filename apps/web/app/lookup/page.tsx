"use client";

import { useCallback, useEffect, useState } from "react";
import { HighlightText } from "@/components/HighlightText";
import { apiFetch, type Term } from "@/lib/api";
import { useRole } from "@/lib/role";

const DEMO =
  "Can we schedule a PIR after the GTM for the BAU runbook? Also check the SLO before the RFC lands.";

export default function LookupPage() {
  const { role, user, jargonAssist } = useRole();
  const [text, setText] = useState(DEMO);
  const [terms, setTerms] = useState<Term[]>([]);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    try {
      const data = await apiFetch<Term[]>("/terms", { role, user });
      setTerms(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }, [role, user]);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <>
      <h1>Lookup</h1>
      <p className="lede">
        Paste chat or doc text. With jargon assist on, approved terms highlight — click for the
        definition.
      </p>
      <div className="panel">
        <label htmlFor="chat">Message / snippet</label>
        <textarea id="chat" value={text} onChange={(e) => setText(e.target.value)} />
        {error && <p className="msg error">{error}</p>}
      </div>
      <div className="panel">
        <h2 style={{ fontSize: "1.1rem" }}>Indexed view</h2>
        <HighlightText text={text} terms={terms} enabled={jargonAssist} />
        {!jargonAssist && <p className="msg">Jargon assist is off — turn it on in the header.</p>}
      </div>
    </>
  );
}
