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
          <Link className="btn primary" href="/upload">
            Upload docs
          </Link>
          <Link className="btn secondary" href="/lookup">
            Try lookup
          </Link>
          <Link className="btn secondary" href="/dictionary">
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
