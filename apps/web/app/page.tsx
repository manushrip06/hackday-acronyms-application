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
          <Link className="primary" href="/upload" style={{ padding: "0.55rem 0.95rem", borderRadius: 10, background: "var(--accent)", color: "#FAF6EC", fontWeight: 700 }}>
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
          Demo flow: pick a team → <strong>Lead</strong> uploads a doc → Review → approve → Dictionary
          and Lookup fill in. Switch Lead / Member in the header.
        </p>
      </div>
    </>
  );
}
