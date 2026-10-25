from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .types import DURABLE_MEMORY


class Memory:
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, unit_id: str) -> Path:
        return self.root / f"{unit_id}.json"

    def load(self, unit_id: str) -> list[dict]:
        path = self._path(unit_id)
        if not path.exists():
            return []
        return json.loads(path.read_text(encoding="utf-8"))

    def _save(self, unit_id: str, rows: list[dict]) -> None:
        self._path(unit_id).write_text(json.dumps(rows, indent=2, default=str), encoding="utf-8")

    def write(self, unit_id: str, kind: str, payload: Any, accepted: bool) -> dict:
        if kind in DURABLE_MEMORY and kind != "acceptance" and not accepted:
            raise PermissionError("durable memory requires acceptance")
        row = {"kind": kind, "payload": payload, "durable": kind in DURABLE_MEMORY}
        rows = self.load(unit_id)
        rows.append(row)
        self._save(unit_id, rows)
        return row

    def commit(self, unit_id: str) -> list[dict]:
        """Disposition flush: keep durable rows, drop scratch."""
        kept = [r for r in self.load(unit_id) if r.get("durable")]
        self._save(unit_id, kept)
        return kept
