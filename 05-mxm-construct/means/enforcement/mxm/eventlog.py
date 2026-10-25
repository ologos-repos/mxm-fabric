"""The kernel's one transactional, append-only event log (ADR-MXK-0003).

Every piece of kernel state (WorkUnits, transitions, challenges, waivers, acceptances,
halts, spent authorizations) and all Evidence is a record in one hash-chained JSONL file,
in the kernel's audit-chain format (mxm/audit_chain.py). A transaction holds an exclusive
lock from reading the log to appending its records, so concurrent kernels sharing a data
root serialize, and each one decides against the state every other one committed.

The optional anchor is the chain head ``{"seq", "hash"}`` kept elsewhere. Verified against
it, the log also detects tail truncation and whole-chain recomputation; that holds only if
the anchor lives where the engine cannot write (a deployment property).
"""
from __future__ import annotations

import fcntl
import json
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

from . import audit_chain


class AnchorError(OSError):
    """The record was appended but the anchor could not be written."""

    def __init__(self, record: dict, cause: Exception):
        super().__init__(f"anchor not written after seq {record['seq']}: {cause}")
        self.record = record


class EventLog:
    def __init__(self, path: str | Path, anchor_path: str | Path | None = None):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.anchor_path = Path(anchor_path) if anchor_path else None
        if self.anchor_path:
            self.anchor_path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def locked(self):
        with open(self.path.with_name(self.path.name + ".lock"), "a+b") as lf:
            fcntl.flock(lf, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(lf, fcntl.LOCK_UN)

    def read_anchor(self) -> tuple[Optional[dict], Optional[str]]:
        """(anchor, None), (None, None) when there is none, or (None, problem). Never raises."""
        if self.anchor_path is None:
            return None, None
        try:
            if not self.anchor_path.exists():
                return None, None
            anchor = json.loads(self.anchor_path.read_text())
        except (OSError, ValueError) as exc:
            return None, f"anchor_unreadable: {exc}"
        if isinstance(anchor, dict) and isinstance(anchor.get("seq"), int) and isinstance(anchor.get("hash"), str):
            return anchor, None
        return None, "anchor_unreadable: not a {seq, hash} object"

    def scan(self) -> tuple[list[dict], list[dict], Optional[dict]]:
        """With the lock held: repair a crash-truncated tail, verify the chain against the
        anchor, and return (records, findings, anchor). Bad content is a finding; only I/O
        errors reading the log raise. With an anchor configured, a log that has records but
        no anchor is a finding too: a deleted anchor must not silently disable the check."""
        anchor, problem = self.read_anchor()
        findings = [{"class": "anchor_unreadable", "line": None, "detail": problem}] if problem else []
        if not self.path.exists():
            if anchor:
                findings.append({"class": "truncated", "line": None, "detail": "log missing but anchored"})
            return [], findings, anchor
        try:
            with open(self.path, "a+b") as f:
                audit_chain.repair_open(f)
        except ValueError:
            pass  # an unparseable last record: verify reports it as corrupt
        result = audit_chain.verify(self.path, anchor=anchor, check_legacy=False)
        records, _ = audit_chain.read(self.path)
        if self.anchor_path is not None and anchor is None and not problem and records:
            findings.append({"class": "anchor_missing", "line": None, "detail": str(self.anchor_path)})
        return [rec for _, rec in records], findings + result["findings"], anchor

    def last(self) -> Optional[dict]:
        if not self.path.exists():
            return None
        with open(self.path, "rb") as f:
            raw, _ = audit_chain._tail(f)
        try:
            return json.loads(raw) if raw else None
        except ValueError:
            return None

    def append(self, fields: dict) -> dict:
        """With the lock held: append one record, then move the anchor to it."""
        with open(self.path, "a+b") as f:
            rec = audit_chain.append_open(f, fields)
        if self.anchor_path is not None:
            try:
                self.write_anchor(rec)
            except OSError as exc:
                raise AnchorError(rec, exc) from exc
        return rec

    def write_anchor(self, rec: dict) -> None:
        tmp = self.anchor_path.with_name(self.anchor_path.name + ".tmp")
        tmp.write_text(json.dumps({"seq": rec["seq"], "hash": rec["hash"]}))
        os.replace(tmp, self.anchor_path)
