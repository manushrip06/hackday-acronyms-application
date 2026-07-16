"use client";

import { useMemo, useState, type ReactNode } from "react";
import type { Term } from "@/lib/api";

type Props = {
  text: string;
  terms: Term[];
  enabled: boolean;
};

export function HighlightText({ text, terms, enabled }: Props) {
  const [active, setActive] = useState<Term | null>(null);
  const [pos, setPos] = useState({ x: 0, y: 0 });

  const sorted = useMemo(
    () =>
      [...terms]
        .filter((t) => t.status === "approved")
        .sort((a, b) => b.term.length - a.term.length),
    [terms]
  );

  const nodes = useMemo(() => {
    if (!enabled || !sorted.length || !text) return [text];
    const pattern = new RegExp(
      `\\b(${sorted.map((t) => escapeRegExp(t.term)).join("|")})\\b`,
      "gi"
    );
    const byLower = new Map(sorted.map((t) => [t.term.toLowerCase(), t]));
    const parts: ReactNode[] = [];
    let last = 0;
    let match: RegExpExecArray | null;
    let key = 0;
    while ((match = pattern.exec(text)) !== null) {
      const start = match.index;
      const end = start + match[0].length;
      if (start > last) parts.push(text.slice(last, start));
      const term = byLower.get(match[0].toLowerCase());
      const slice = text.slice(start, end);
      if (term) {
        parts.push(
          <span
            key={key++}
            className="term-hit"
            onClick={(e) => {
              setActive(term);
              setPos({ x: e.clientX, y: e.clientY });
            }}
          >
            {slice}
          </span>
        );
      } else {
        parts.push(slice);
      }
      last = end;
    }
    if (last < text.length) parts.push(text.slice(last));
    return parts;
  }, [text, sorted, enabled]);

  return (
    <div className="lookup-surface">
      {nodes}
      {active && (
        <div
          className="popover"
          style={{ left: Math.min(pos.x - 40, window.innerWidth - 340), top: pos.y + 12 }}
          onClick={() => setActive(null)}
        >
          <strong>{active.term}</strong>
          <p style={{ margin: "0.4rem 0 0", color: "var(--muted)" }}>{active.definition}</p>
          <p style={{ margin: "0.5rem 0 0", fontSize: "0.8rem", color: "var(--muted)" }}>
            Click to dismiss
          </p>
        </div>
      )}
    </div>
  );
}

function escapeRegExp(s: string) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}
