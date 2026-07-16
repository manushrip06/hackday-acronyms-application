"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { Term } from "@/lib/api";
import { buildTermIndex, findTerm, normalizeSelection } from "@/lib/termLookup";

type PopoverState = {
  term: Term | null;
  query: string;
  x: number;
  y: number;
};

type Props = {
  text: string;
  terms: Term[];
  enabled: boolean;
  className?: string;
};

export function SelectionLookupText({ text, terms, enabled, className }: Props) {
  const ref = useRef<HTMLDivElement>(null);
  const index = useMemo(() => buildTermIndex(terms), [terms]);
  const [popover, setPopover] = useState<PopoverState | null>(null);

  useEffect(() => {
    if (!enabled) setPopover(null);
  }, [enabled]);

  const lookupSelection = useCallback(() => {
    if (!enabled || !ref.current) return;

    const sel = window.getSelection();
    if (!sel || sel.isCollapsed) return;

    const anchor = sel.anchorNode;
    if (!anchor || !ref.current.contains(anchor)) return;

    const raw = sel.toString();
    const query = normalizeSelection(raw);
    if (!query) return;

    let match = findTerm(query, index);
    if (!match && query.includes(" ")) {
      const first = normalizeSelection(query.split(/\s+/)[0] ?? "");
      if (first) {
        match = findTerm(first, index);
      }
    }

    const range = sel.getRangeAt(0);
    const rect = range.getBoundingClientRect();
    if (!rect.width && !rect.height) return;

    setPopover({
      term: match,
      query: match?.term ?? query,
      x: Math.min(Math.max(rect.left, 12), window.innerWidth - 332),
      y: rect.bottom + 8,
    });
  }, [enabled, index]);

  return (
    <>
      <div
        ref={ref}
        className={`lookup-surface selectable-text ${className ?? ""}`.trim()}
        onMouseUp={lookupSelection}
      >
        {text}
      </div>
      {popover && enabled && (
        <>
          <button
            type="button"
            className="popover-backdrop"
            aria-label="Dismiss definition"
            onClick={() => setPopover(null)}
          />
          <div
            className="popover popover-fixed"
            style={{ left: popover.x, top: popover.y }}
            role="dialog"
          >
            {popover.term ? (
              <>
                <strong>{popover.term.term}</strong>
                <p style={{ margin: "0.4rem 0 0", color: "var(--muted)" }}>
                  {popover.term.definition}
                </p>
              </>
            ) : (
              <>
                <strong>{popover.query}</strong>
                <p style={{ margin: "0.4rem 0 0", color: "var(--muted)" }}>
                  Not in the team dictionary yet.
                </p>
              </>
            )}
            <p style={{ margin: "0.5rem 0 0", fontSize: "0.8rem", color: "var(--muted)" }}>
              Click outside to dismiss
            </p>
          </div>
        </>
      )}
    </>
  );
}
