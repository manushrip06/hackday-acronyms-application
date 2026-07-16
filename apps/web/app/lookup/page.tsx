"use client";

import { useCallback, useEffect, useState } from "react";
import { MockChat, type ChatMessage } from "@/components/MockChat";
import { SelectionLookupText } from "@/components/SelectionLookupText";
import { apiFetch, type Term } from "@/lib/api";
import { useRole } from "@/lib/role";

const DEMO =
  "Can we schedule a PIR after the GTM for the BAU runbook? Also check the SLO before the RFC lands.";

const MOCK_MESSAGES: ChatMessage[] = [
  {
    id: "1",
    author: "Alex Chen",
    time: "10:02 AM",
    text: "Can we schedule a PIR after the GTM for the BAU runbook?",
  },
  {
    id: "2",
    author: "Jordan Lee",
    time: "10:04 AM",
    text: "What's the RFC status? We need to hit the SLO before GA.",
  },
  {
    id: "3",
    author: "Sam Rivera",
    time: "10:06 AM",
    text: "New hire question — what does OKR mean in our planning docs?",
  },
];

export default function LookupPage() {
  const { role, user, jargonAssist } = useRole();
  const [text, setText] = useState(DEMO);
  const [terms, setTerms] = useState<Term[]>([]);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setError("");
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
        Like Google — double-click a word or drag to highlight it. Definitions come from your team
        dictionary in the database (approved terms only).
      </p>

      {error && <p className="msg error">{error}</p>}

      <MockChat messages={MOCK_MESSAGES} terms={terms} enabled={jargonAssist} />

      {!jargonAssist && (
        <p className="msg">Jargon assist is off — turn it on in the header to look up words.</p>
      )}

      <div className="panel">
        <label htmlFor="chat">Or paste your own message / snippet</label>
        <textarea id="chat" value={text} onChange={(e) => setText(e.target.value)} />
      </div>
      {text.trim() && (
        <div className="panel">
          <h2 style={{ fontSize: "1.1rem" }}>Preview — select text below</h2>
          <SelectionLookupText text={text} terms={terms} enabled={jargonAssist} />
        </div>
      )}
    </>
  );
}