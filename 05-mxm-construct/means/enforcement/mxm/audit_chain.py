"""Hash-chained floor audit (REQ-STO-07, WP-TMH-0007). Stdlib only.

Every record is one JSON line. Its ``hash`` is sha256 over the canonical JSON of the
record without the ``hash`` key (sorted keys, compact separators, UTF-8). Each record
carries ``prev_hash`` (the previous record's ``hash``; 64 zeros for the first) and a
strictly increasing ``seq`` starting at 1. Editing, deleting or reordering a record
breaks the chain; truncating the tail, or recomputing every hash after an edit, is
detectable only against an anchor held elsewhere (a checkpoint: scripts/checkpoint.py).

Record schema (``v`` = 1):

    v, seq, ts (UTC ISO-8601), prev_hash, hash,
    kind       "verdict" | "genesis" | "repair" | "record_store"
    verdict    kind=verdict: "deny" | "override"; kind=record_store: the action
    rule, reason, overridable, justification, command, grant ({id, scope, recorded_at}|null)
    grant_used true when an override was backed by a recorded grant
    operator   {"username": str, "role": str}   ("unknown" when not supplied)
    engine, run_id                               (null when not supplied)

Identity contract: the launching surface (the console, per turn) sets MXM_OPERATOR,
MXM_OPERATOR_ROLE, MXM_ENGINE and MXM_RUN_ID in the engine's environment. Absent
values are recorded as "unknown" / null, never inferred from the host.

Legacy migration: if the chain is empty and the pre-chain plain audit log exists, the
first record is a sealed ``genesis`` record carrying that file's path, sha256 and line
count. The legacy file is kept unchanged; verify-audit.py can re-check its digest.
"""
import datetime
import fcntl
import hashlib
import json
import os
import pathlib

ZERO = "0" * 64
SCHEMA = 1


def canonical(record):
    body = {k: v for k, v in record.items() if k != "hash"}
    return json.dumps(body, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def record_hash(record):
    return hashlib.sha256(canonical(record)).hexdigest()


def identity(env=None):
    env = os.environ if env is None else env
    return {"operator": {"username": env.get("MXM_OPERATOR") or "unknown",
                         "role": env.get("MXM_OPERATOR_ROLE") or "unknown"},
            "engine": env.get("MXM_ENGINE") or None,
            "run_id": env.get("MXM_RUN_ID") or None}


def chain_path(policy):
    """MXM_AUDIT_CHAIN, else the policy's ``audit_chain``, else beside the legacy log."""
    raw = os.environ.get("MXM_AUDIT_CHAIN") or policy.get("audit_chain")
    if raw:
        return pathlib.Path(raw).expanduser()
    legacy = pathlib.Path(policy.get("audit_log", "~/.mxm/override-audit.log")).expanduser()
    return legacy.with_name("audit-chain.jsonl")


def legacy_path(policy):
    raw = policy.get("audit_log")
    return pathlib.Path(raw).expanduser() if raw else None


def file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(65536), b""):
            h.update(block)
    return h.hexdigest()


def _tail(f):
    """Return (last complete line bytes or None, offset where a partial tail starts or None)."""
    f.seek(0, os.SEEK_END)
    size = f.tell()
    if size == 0:
        return None, None
    f.seek(size - 1)
    partial_at = None
    end = size
    if f.read(1) != b"\n":
        # Crash mid-append: bytes after the last newline are an incomplete record.
        pos = _rfind_newline(f, size)
        partial_at = pos + 1
        end = partial_at
        if end == 0:
            return None, 0
    start = _rfind_newline(f, end - 1) + 1
    f.seek(start)
    return f.read(end - 1 - start), partial_at


def _rfind_newline(f, before):
    """Offset of the last b"\\n" strictly before ``before``, or -1."""
    pos = before
    while pos > 0:
        step = min(65536, pos)
        pos -= step
        f.seek(pos)
        i = f.read(step).rfind(b"\n")
        if i != -1:
            return pos + i
    return -1


def _now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _seal(prev, fields):
    rec = {"v": SCHEMA, "seq": (prev["seq"] + 1) if prev else 1, "ts": _now(),
           "prev_hash": prev["hash"] if prev else ZERO}
    rec.update(fields)
    rec["hash"] = record_hash(rec)
    return rec


def _write(f, rec):
    f.write(json.dumps(rec, sort_keys=True, ensure_ascii=False).encode("utf-8") + b"\n")
    f.flush()
    os.fsync(f.fileno())


def repair_open(f, env=None):
    """With the append lock held and ``f`` opened "a+b": if a crash left an incomplete
    trailing record, discard it and seal a ``repair`` record. Returns the last record."""
    last, partial_at = _tail(f)
    prev = json.loads(last) if last else None
    if partial_at is not None:
        f.seek(partial_at)
        fragment = f.read()
        f.truncate(partial_at)
        prev = _seal(prev, {"kind": "repair",
                            "reason": "incomplete trailing record discarded",
                            "discarded": fragment.decode("utf-8", "replace"),
                            **identity(env)})
        _write(f, prev)
    return prev


def append_open(f, fields, legacy=None, legacy_target=None, env=None):
    """Append one record to ``f`` (opened "a+b") with the append lock already held."""
    fields = dict(fields)
    for k, v in identity(env).items():
        fields.setdefault(k, v)
    prev = repair_open(f, env)
    if prev is None and legacy is not None and pathlib.Path(legacy).is_file() \
            and (legacy_target is None or pathlib.Path(legacy).resolve() != legacy_target.resolve()):
        lp = pathlib.Path(legacy)
        with open(lp, "rb") as lfh:
            lines = sum(1 for _ in lfh)
        prev = _seal(None, {"kind": "genesis",
                            "reason": "pre-chain plain audit log sealed",
                            "legacy_path": str(lp),
                            "legacy_sha256": file_sha256(lp),
                            "legacy_lines": lines, **identity(env)})
        _write(f, prev)
    rec = _seal(prev, fields)
    _write(f, rec)
    return rec


def append(path, fields, legacy=None, env=None):
    """Append one record under an exclusive lock and return it. ``fields`` must not
    set seq/ts/prev_hash/hash. Identity fields are filled from the environment when
    the caller does not supply them."""
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lock = path.with_name(path.name + ".lock")
    with open(lock, "a+b") as lf:
        fcntl.flock(lf, fcntl.LOCK_EX)
        try:
            with open(path, "a+b") as f:
                return append_open(f, fields, legacy=legacy, legacy_target=path, env=env)
        finally:
            fcntl.flock(lf, fcntl.LOCK_UN)


def read(path):
    """Return (records, problems) where problems are unparseable lines."""
    records, problems = [], []
    with open(path, "rb") as f:
        for n, raw in enumerate(f, 1):
            line = raw.rstrip(b"\n")
            if not line.strip():
                problems.append(("blank", n, "blank line"))
                continue
            try:
                records.append((n, json.loads(line)))
            except ValueError:
                problems.append(("corrupt", n, "unparseable record"))
    return records, problems


def verify(path, anchor=None, check_legacy=True):
    """Verify a chain. ``anchor`` is {"seq": int, "hash": str} from a checkpoint.
    Returns {"ok": bool, "records": int, "head": {...}|None, "findings": [...]} where
    each finding is {"class", "line", "detail"}; classes: corrupt, edited, deleted,
    reordered, truncated, rewritten, legacy_modified."""
    findings = []
    records, problems = read(path)
    for cls, line, detail in problems:
        findings.append({"class": "corrupt", "line": line, "detail": detail})
    prev = None
    seen = {}
    order = []
    for line, rec in records:
        stored = rec.get("hash")
        if stored != record_hash(rec):
            findings.append({"class": "edited", "line": line,
                             "detail": f"seq {rec.get('seq')}: content does not match its hash"})
        seq = rec.get("seq")
        if not isinstance(seq, int) or isinstance(seq, bool):
            findings.append({"class": "corrupt", "line": line, "detail": "missing seq"})
            prev = rec
            continue
        order.append(seq)
        seen.setdefault(seq, stored)
        # A link that breaks while the sequence number is exactly the next one is a
        # replaced record (edit with a recomputed hash); gaps and inversions are
        # classified globally below.
        exp_seq = (prev.get("seq", 0) + 1) if prev else 1
        exp_prev = prev.get("hash") if prev else ZERO
        if seq == exp_seq and rec.get("prev_hash") != exp_prev:
            findings.append({"class": "edited", "line": line,
                             "detail": f"seq {seq}: prev_hash does not link to seq {exp_seq - 1}"})
        prev = rec
    if order:
        missing = sorted(set(range(1, max(order) + 1)) - set(order))
        if missing:
            findings.append({"class": "deleted", "line": None,
                             "detail": f"missing seq {_ranges(missing)}"})
        inversions = [(a, b) for a, b in zip(order, order[1:]) if b <= a]
        if inversions:
            findings.append({"class": "reordered", "line": None,
                             "detail": "out of order: " + ", ".join(
                                 f"{b} after {a}" for a, b in inversions[:5])})
    head = {"seq": prev.get("seq"), "hash": prev.get("hash")} if prev else None
    if anchor:
        a_seq, a_hash = anchor.get("seq"), anchor.get("hash")
        if a_seq and (head is None or (head.get("seq") or 0) < a_seq):
            findings.append({"class": "truncated", "line": None,
                             "detail": f"chain ends at seq {head and head.get('seq')}, "
                                       f"anchor records seq {a_seq}"})
        elif a_seq and seen.get(a_seq) != a_hash:
            findings.append({"class": "rewritten", "line": None,
                             "detail": f"record seq {a_seq} hash differs from the anchor"})
    if check_legacy and records:
        g = records[0][1]
        if g.get("kind") == "genesis" and g.get("legacy_path"):
            lp = pathlib.Path(g["legacy_path"])
            if lp.is_file() and file_sha256(lp) != g.get("legacy_sha256"):
                findings.append({"class": "legacy_modified", "line": records[0][0],
                                 "detail": f"{lp} no longer matches its sealed sha256"})
    return {"ok": not findings, "records": len(records), "head": head, "findings": findings}


def _ranges(nums):
    out, start = [], nums[0]
    for a, b in zip(nums, nums[1:] + [None]):
        if b != a + 1:
            out.append(str(start) if start == a else f"{start}-{a}")
            start = b
    return ",".join(out)


def head(path):
    """Current head {"seq", "hash"} or None, read under the append lock."""
    path = pathlib.Path(path)
    if not path.is_file():
        return None
    with open(path.with_name(path.name + ".lock"), "a+b") as lf:
        fcntl.flock(lf, fcntl.LOCK_SH)
        try:
            with open(path, "rb") as f:
                last, _ = _tail(f)
        finally:
            fcntl.flock(lf, fcntl.LOCK_UN)
    if not last:
        return None
    rec = json.loads(last)
    return {"seq": rec.get("seq"), "hash": rec.get("hash")}


SYSLOG_FACILITY = 13  # RFC 5424 "log audit"
_SEVERITY = {"deny": 4, "override": 5}
SD_ID = "mxm@32473"   # 32473 is the documentation-reserved enterprise number (RFC 5612)


def _sd_escape(value):
    return str(value).replace("\\", "\\\\").replace('"', '\\"').replace("]", "\\]")


def to_syslog(rec, hostname="-", app="mxm-floor"):
    """One RFC 5424 line: <PRI>1 TS HOST APP - MSGID [mxm@32473 ...] MSG."""
    verdict = rec.get("verdict") or rec.get("kind") or "-"
    sev = _SEVERITY.get(rec.get("verdict"), 6)
    op = rec.get("operator") or {}
    params = [("seq", rec.get("seq")), ("hash", rec.get("hash")),
              ("prev", rec.get("prev_hash")), ("kind", rec.get("kind")),
              ("verdict", rec.get("verdict")), ("rule", rec.get("rule")),
              ("overridable", rec.get("overridable")),
              ("operator", op.get("username")), ("role", op.get("role")),
              ("engine", rec.get("engine")), ("run", rec.get("run_id")),
              ("grant", (rec.get("grant") or {}).get("id"))]
    sd = "[" + SD_ID + "".join(f' {k}="{_sd_escape(v)}"' for k, v in params
                               if v is not None) + "]"
    msgid = "".join(c for c in str(verdict) if 33 <= ord(c) <= 126)[:32] or "-"
    msg = " ".join(str(rec.get("reason") or "").split())
    return (f"<{SYSLOG_FACILITY * 8 + sev}>1 {rec.get('ts', '-')} {hostname or '-'} "
            f"{app} - {msgid} {sd}" + (f" {msg}" if msg else ""))
