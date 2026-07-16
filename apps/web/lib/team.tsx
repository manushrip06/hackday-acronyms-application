"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";

export const MOCK_TEAMS = [
  { id: "default", name: "Engineering" },
  { id: "sales", name: "Sales" },
] as const;

export type TeamId = (typeof MOCK_TEAMS)[number]["id"];

type Ctx = {
  teamId: TeamId;
  setTeamId: (id: TeamId) => void;
  activeTeam: (typeof MOCK_TEAMS)[number];
};

const TeamContext = createContext<Ctx | null>(null);

export function TeamProvider({ children }: { children: ReactNode }) {
  const [teamId, setTeamIdState] = useState<TeamId>("default");

  useEffect(() => {
    const saved = localStorage.getItem("ha-team-id");
    if (saved === "default" || saved === "sales") setTeamIdState(saved);
  }, []);

  const setTeamId = useCallback((id: TeamId) => {
    setTeamIdState(id);
    localStorage.setItem("ha-team-id", id);
  }, []);

  const activeTeam = useMemo(
    () => MOCK_TEAMS.find((t) => t.id === teamId) ?? MOCK_TEAMS[0],
    [teamId]
  );

  const value = useMemo(() => ({ teamId, setTeamId, activeTeam }), [teamId, setTeamId, activeTeam]);

  return <TeamContext.Provider value={value}>{children}</TeamContext.Provider>;
}

export function useTeam() {
  const ctx = useContext(TeamContext);
  if (!ctx) throw new Error("useTeam must be used within TeamProvider");
  return ctx;
}
