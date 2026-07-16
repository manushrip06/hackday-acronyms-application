import Link from "next/link";

export default function HomePage() {
  return (
    <>
      <h1>Team jargon, indexed</h1>
      <p className="lede">
        Leads upload documentation. The pipeline extracts acronyms and domain terms, drafts
        definitions, and waits for review. Anyone can look up unclear words — in the web app or a
        sideloaded Teams personal tab.
      </p>
      <div className="panel">
        <div className="row">
          <Link className="primary" href="/upload" style={{ padding: "0.55rem 0.95rem", borderRadius: 10, background: "var(--accent)", color: "#06241c", fontWeight: 700 }}>
            Upload docs
          </Link>
          <Link href="/lookup" style={{ padding: "0.55rem 0.95rem", borderRadius: 10, border: "1px solid var(--line)", fontWeight: 700 }}>
            Try lookup
          </Link>
          <Link href="/dictionary" style={{ padding: "0.55rem 0.95rem", borderRadius: 10, border: "1px solid var(--line)", fontWeight: 700 }}>
            Dictionary
          </Link>
        </div>
        <p className="msg">
          Demo tip: switch Lead / Member in the header. Auth is hackday-simple via{" "}
          <code>X-Role</code> headers.
        </p>
      </div>
    </>
  );
}
