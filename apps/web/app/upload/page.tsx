"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { apiFetch, type UploadResult } from "@/lib/api";
import { useRole } from "@/lib/role";
import { useTeam } from "@/lib/team";

export default function UploadPage() {
  const { role, user } = useRole();
  const { teamId, activeTeam } = useTeam();
  const [file, setFile] = useState<File | null>(null);
  const [paste, setPaste] = useState("");
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function onUpload(e: FormEvent) {
    e.preventDefault();
    setError("");
    setMsg("");
    if (role !== "lead") {
      setError("Switch to Lead to upload documentation.");
      return;
    }
    setBusy(true);
    try {
      let result: UploadResult;
      if (file) {
        const fd = new FormData();
        fd.append("file", file);
        result = await apiFetch<UploadResult>("/documents/upload", {
          method: "POST",
          role,
          user,
          teamId,
          body: fd,
        });
      } else if (paste.trim()) {
        result = await apiFetch<UploadResult>("/documents/paste", {
          method: "POST",
          role,
          user,
          teamId,
          body: JSON.stringify({ text: paste, filename: "pasted.txt" }),
        });
      } else {
        setError("Choose a file or paste text.");
        setBusy(false);
        return;
      }
      setMsg(
        `Uploaded ${result.filename} for ${activeTeam.name}\n` +
          `Candidates: ${result.candidates_found}\n` +
          `Pending created: ${result.pending_created}, updated: ${result.pending_updated}\n` +
          `→ Approve in Review before terms show in Dictionary.`
      );
      setFile(null);
      setPaste("");
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <h1>Upload documentation</h1>
      <p className="lede">
        Lead-only for <strong>{activeTeam.name}</strong>. After upload, open <strong>Review</strong>{" "}
        to approve terms — then they appear in Dictionary and Lookup.
      </p>
      <form className="panel" onSubmit={onUpload}>
        <label htmlFor="file">File (.md, .txt, .pdf)</label>
        <input
          id="file"
          type="file"
          accept=".md,.txt,.text,.pdf,.csv"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
        />
        <div style={{ height: "1rem" }} />
        <label htmlFor="paste">Or paste text</label>
        <textarea
          id="paste"
          value={paste}
          onChange={(e) => setPaste(e.target.value)}
          placeholder="Paste team wiki excerpt…"
        />
        <div className="row" style={{ marginTop: "1rem" }}>
          <button className="primary" type="submit" disabled={busy}>
            {busy ? "Extracting…" : "Upload & extract"}
          </button>
        </div>
        {msg && (
          <div className="msg">
            <p style={{ margin: 0, whiteSpace: "pre-wrap" }}>{msg}</p>
            <Link
              href="/review"
              className="primary"
              style={{
                display: "inline-block",
                marginTop: "0.75rem",
                padding: "0.55rem 0.95rem",
                borderRadius: 10,
                fontWeight: 700,
              }}
            >
              Open Review queue →
            </Link>
          </div>
        )}
        {error && <p className="msg error">{error}</p>}
      </form>
    </>
  );
}
