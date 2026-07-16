"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useRole } from "@/lib/role";

const links = [
  { href: "/", label: "Home" },
  { href: "/upload", label: "Upload" },
  { href: "/review", label: "Review" },
  { href: "/dictionary", label: "Dictionary" },
  { href: "/lookup", label: "Lookup" },
];

export function Nav() {
  const pathname = usePathname();
  const { role, setRole, jargonAssist, setJargonAssist } = useRole();

  return (
    <header className="nav">
      <div className="brand">
        Acronym <span>Atlas</span>
      </div>
      <nav className="nav-links">
        {links.map((l) => (
          <Link key={l.href} href={l.href} className={pathname === l.href ? "active" : ""}>
            {l.label}
          </Link>
        ))}
      </nav>
      <div className="controls">
        <button
          type="button"
          className={`pill ${role === "lead" ? "active" : ""}`}
          onClick={() => setRole("lead")}
        >
          Lead
        </button>
        <button
          type="button"
          className={`pill ${role === "member" ? "active" : ""}`}
          onClick={() => setRole("member")}
        >
          Member
        </button>
        <button
          type="button"
          className={`pill ${jargonAssist ? "active" : ""}`}
          onClick={() => setJargonAssist(!jargonAssist)}
        >
          Jargon assist {jargonAssist ? "on" : "off"}
        </button>
      </div>
    </header>
  );
}
