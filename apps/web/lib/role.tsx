"use client";

import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import type { Role } from "./api";

type Ctx = {
  role: Role;
  setRole: (r: Role) => void;
  user: string;
  setUser: (u: string) => void;
  jargonAssist: boolean;
  setJargonAssist: (v: boolean) => void;
};

const RoleContext = createContext<Ctx | null>(null);

export function RoleProvider({ children }: { children: ReactNode }) {
  const [role, setRoleState] = useState<Role>("lead");
  const [user, setUserState] = useState("demo-lead");
  const [jargonAssist, setJargonAssistState] = useState(true);

  useEffect(() => {
    const r = localStorage.getItem("ha-role") as Role | null;
    const u = localStorage.getItem("ha-user");
    const j = localStorage.getItem("ha-jargon");
    if (r === "lead" || r === "member") setRoleState(r);
    if (u) setUserState(u);
    if (j != null) setJargonAssistState(j === "1");
  }, []);

  const value = useMemo<Ctx>(
    () => ({
      role,
      setRole: (r) => {
        setRoleState(r);
        localStorage.setItem("ha-role", r);
        if (r === "lead") {
          setUserState("demo-lead");
          localStorage.setItem("ha-user", "demo-lead");
        } else {
          setUserState("demo-member");
          localStorage.setItem("ha-user", "demo-member");
        }
      },
      user,
      setUser: (u) => {
        setUserState(u);
        localStorage.setItem("ha-user", u);
      },
      jargonAssist,
      setJargonAssist: (v) => {
        setJargonAssistState(v);
        localStorage.setItem("ha-jargon", v ? "1" : "0");
      },
    }),
    [role, user, jargonAssist]
  );

  return <RoleContext.Provider value={value}>{children}</RoleContext.Provider>;
}

export function useRole() {
  const ctx = useContext(RoleContext);
  if (!ctx) throw new Error("useRole must be used within RoleProvider");
  return ctx;
}
