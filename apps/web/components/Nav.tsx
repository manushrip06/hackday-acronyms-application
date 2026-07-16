"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useRole } from "@/lib/role";
import { MOCK_TEAMS, useTeam, type TeamId } from "@/lib/team";

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
  const { teamId, setTeamId, activeTeam } = useTeam();

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
        <label htmlFor="team-select" className="sr-only">
          Team
        </label>
        <select
          id="team-select"
          className="team-select"
          value={teamId}
          onChange={(e) => setTeamId(e.target.value as TeamId)}
        >
          {MOCK_TEAMS.map((t) => (
            <option key={t.id} value={t.id}>
              {t.name}
            </option>
          ))}
        </select>
        <span className="team-badge">{activeTeam.name}</span>
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
