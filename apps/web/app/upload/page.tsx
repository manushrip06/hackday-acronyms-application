"use client";

import { FormEvent, useState } from "react";
import { apiFetch, type UploadResult } from "@/lib/api";
import { useRole } from "@/lib/role";

export default function UploadPage() {
  const { role, user } = useRole();
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
          body: fd,
        });
      } else if (paste.trim()) {
        result = await apiFetch<UploadResult>("/documents/paste", {
          method: "POST",
          role,
          user,
          body: JSON.stringify({ text: paste, filename: "pasted.txt" }),
        });
      } else {
        setError("Choose a file or paste text.");
        setBusy(false);
        return;
      }
      setMsg(
        `Uploaded ${result.filename}\n` +
          `Candidates: ${result.candidates_found}\n` +
          `Pending created: ${result.pending_created}, updated: ${result.pending_updated}\n` +
          `Conflicts: ${result.conflicts}, approved left alone: ${result.approved_unchanged}\n` +
          `→ Open Review to approve.`
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
        Lead-only. Upload Markdown/text/PDF or paste wiki text. Extraction merges new pending terms
        without wiping approved ones.
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
        {msg && <p className="msg">{msg}</p>}
        {error && <p className="msg error">{error}</p>}
      </form>
    </>
  );
}
