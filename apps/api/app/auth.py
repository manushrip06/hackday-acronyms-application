from dataclasses import dataclass

from fastapi import Header, HTTPException

from .config import get_settings
from .schemas import Role

MOCK_TEAM_IDS = frozenset({"default", "sales"})


@dataclass
class Actor:
    role: Role
    user: str


def get_actor(
    x_role: str = Header(default="member", alias="X-Role"),
    x_user: str = Header(default="anonymous", alias="X-User"),
) -> Actor:
    role = (x_role or "member").strip().lower()
    if role not in ("lead", "member"):
        raise HTTPException(status_code=400, detail="X-Role must be 'lead' or 'member'")
    return Actor(role=role, user=(x_user or "anonymous").strip() or "anonymous")


def require_lead(actor: Actor) -> Actor:
    if actor.role != "lead":
        raise HTTPException(status_code=403, detail="Lead role required")
    return actor


def get_team_id(
    x_team_id: str | None = Header(default=None, alias="X-Team-Id"),
) -> str:
    settings = get_settings()
    team_id = (x_team_id or settings.team_id or "default").strip().lower()
    if team_id not in MOCK_TEAM_IDS:
        raise HTTPException(status_code=400, detail="Unknown team; use default or sales")
    return team_id
