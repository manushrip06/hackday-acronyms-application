"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useRole } from "@/lib/role";
import { useEffect, useState } from "react";

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

  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", darkMode);
  }, [darkMode]);

  return (
    <header className="nav">
      <Link href="/" className="brand">
      <img
        src="/state-farm-logo.png"
        alt="State Farm logo"
        className="brand-logo"
      />
      <span>
        Acronym <span>Atlas</span>
      </span>
</Link>
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
      className="pill"
      onClick={() => setDarkMode(!darkMode)}
       >
      {darkMode ? "☀ Light" : "🌙 Dark"}
       </button>
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
