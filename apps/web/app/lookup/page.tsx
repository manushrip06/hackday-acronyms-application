"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { MockChat, type ChatMessage } from "@/components/MockChat";
import { SelectionLookupText } from "@/components/SelectionLookupText";
import { apiFetch, type Term } from "@/lib/api";
import { useRole } from "@/lib/role";
import { useTeam } from "@/lib/team";

const ENGINEERING_MESSAGES: ChatMessage[] = [
  {
    id: "1",
    author: "Alex Chen",
    time: "10:02 AM",
    text: "Can we schedule a PIR after the GTM launch? Keep BAU changes out of the release window.",
  },
  {
    id: "2",
    author: "Jordan Lee",
    time: "10:04 AM",
    text: "RFC is still in review — we need to hit the SLO before we ship.",
  },
  {
    id: "3",
    author: "Sam Rivera",
    time: "10:06 AM",
    text: "Planning doc question: how do OKRs tie into our quarterly roadmap?",
  },
];

const SALES_MESSAGES: ChatMessage[] = [
  {
    id: "1",
    author: "Morgan Blake",
    time: "9:15 AM",
    text: "Log this in the CRM — webinar lead is an MQL and matches our ICP.",
  },
  {
    id: "2",
    author: "Taylor Kim",
    time: "9:18 AM",
    text: "Once it's an SQL, hand it to the AE. We're tracking ARR impact this quarter.",
  },
  {
    id: "3",
    author: "Chris Park",
    time: "9:21 AM",
    text: "Can we review MQL vs SQL criteria again in standup?",
  },
];

export default function LookupPage() {
  const { role, user, jargonAssist } = useRole();
  const { teamId, activeTeam } = useTeam();
  const [text, setText] = useState("");
  const [terms, setTerms] = useState<Term[]>([]);
  const [error, setError] = useState("");

  const messages = useMemo(
    () => (teamId === "sales" ? SALES_MESSAGES : ENGINEERING_MESSAGES),
    [teamId]
  );

  useEffect(() => {
    setText(messages[0]?.text ?? "");
  }, [messages]);

  const load = useCallback(async () => {
    setError("");
    try {
      const data = await apiFetch<Term[]>("/terms", { role, user, teamId });
      setTerms(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }, [role, user, teamId]);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <>
      <h1>Lookup</h1>
      <p className="lede">
        <strong>{activeTeam.name}</strong> — double-click a word or drag to highlight it. Only
        approved terms from this team&apos;s dictionary work (upload → Review → approve first).
      </p>

      {error && <p className="msg error">{error}</p>}

      {!terms.length && !error && (
        <p className="msg">No approved terms yet — upload as Lead, approve in Review, then try lookup.</p>
      )}

      <MockChat
        messages={messages}
        terms={terms}
        enabled={jargonAssist}
        channelName={activeTeam.name.toLowerCase().replace(/\s+/g, "-")}
      />

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
