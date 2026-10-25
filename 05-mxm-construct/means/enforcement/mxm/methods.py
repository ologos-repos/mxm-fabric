from __future__ import annotations

from typing import Any, Callable


class MethodRegistry:
    def __init__(self):
        self._by_id: dict[str, Callable[[dict], Any]] = {}
        self._by_type: dict[str, str] = {}

    def register(self, method_id: str, unit_type: str, fn: Callable[[dict], Any]) -> None:
        self._by_id[method_id] = fn
        self._by_type[unit_type] = method_id

    def has(self, method_id: str) -> bool:
        return method_id in self._by_id

    def required_for(self, unit_type: str) -> str | None:
        return self._by_type.get(unit_type)

    def run(self, method_id: str, args: dict) -> Any:
        if method_id not in self._by_id:
            raise KeyError(method_id)
        return self._by_id[method_id](args)
