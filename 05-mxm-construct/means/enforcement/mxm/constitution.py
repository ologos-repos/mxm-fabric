from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


@dataclass(frozen=True)
class Constitution:
    version: str
    mind: str
    mission: dict
    morals: dict
    path: str = ""

    def document(self) -> dict:
        return {
            "version": self.version,
            "mind": self.mind,
            "mission": self.mission,
            "morals": self.morals,
        }

    def pin(self) -> str:
        return hashlib.sha256(_canonical(self.document()).encode("utf-8")).hexdigest()

    def render(self) -> str:
        mission = self.mission
        return (
            "# Mind\n"
            f"{self.mind.strip()}\n\n"
            "# Mission\n"
            f"Identity: {mission.get('identity', '')}\n"
            f"Scope: {mission.get('scope', '')}\n"
            f"Role: {mission.get('role', '')}\n\n"
            "# Morals\n"
            "You propose. The kernel commits. You do not hold terminal authority.\n"
            f"Attribution of all work product: {self.morals.get('attribution', '')}\n"
        )

    @classmethod
    def load(cls, path: str | Path) -> "Constitution":
        path = Path(path)
        data = json.loads(path.read_text(encoding="utf-8"))
        for key in ("version", "mind", "mission", "morals"):
            if key not in data:
                raise ValueError(f"constitution missing {key}")
        return cls(
            version=data["version"],
            mind=data["mind"],
            mission=data["mission"],
            morals=data["morals"],
            path=str(path),
        )
