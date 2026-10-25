import shutil, subprocess, pathlib, sys
src = pathlib.Path("enforcement")
M = {
 "replay signature check": ("mxm/kernel.py", "            if problem:\n                raise InvalidRecord(f\"authorization {problem}\")", "            pass"),
 "effect ownership by role": ("mxm/kernel.py", "                raise InvalidRecord(f\"{effect} is the {owner}'s act\")", "                pass"),
 "transition check on replay": ("mxm/kernel.py", "        if unit is not None:\n            self._check_transition(unit, actor, effects)", "        pass"),
 "port authorization": ("mxm/kernel.py", "                if problem:\n                    return self._commit(unit_id, action, None, None, _deny(f\"unverified_{action.actor}\"), problem)", "                pass"),
 "single use": ("mxm/authz.py", "    if auth_id in consumed:\n        return None, \"replayed\"", "    pass"),
 "act binding": ("mxm/authz.py", "    if mismatch:\n        return None, \"act_mismatch\"", "    pass"),
 "unit binding": ("mxm/authz.py", "    if body.get(\"unit_id\") != unit_id:\n        return None, \"wrong_unit\"", "    pass"),
 "pin binding": ("mxm/authz.py", "    if pin is not None and body.get(\"pin\") != pin:\n        return None, \"wrong_pin\"", "    pass"),
 "expiry": ("mxm/authz.py", "    if now is not None and not (issued - CLOCK_SKEW <= now <= expires):\n        return None, \"expired\"", "    pass"),
 "signature validity": ("mxm/authz.py", "    if not ed25519.verify(key.public, signed, sig):", "    if False:"),
 "key role": ("mxm/authz.py", "    if key.role != role or body.get(\"role\") != role:", "    if False:"),
 "key retirement": ("mxm/authz.py", "    if key.valid_through_seq is not None and seq > key.valid_through_seq:", "    if False:"),
 "chain verification": ("mxm/eventlog.py", "        return [rec for _, rec in records], findings + result[\"findings\"], anchor", "        return [rec for _, rec in records], findings, anchor"),
 "in-process prefix check": ("mxm/kernel.py", "            return self._set_fatal(\"evidence_rewritten\", {\"applied_seq\": seq})", "            pass"),
 "ed25519 S < L": ("mxm/ed25519.py", "    if s >= L:\n        return False", "    pass"),
 "new unit id on open": ("mxm/kernel.py", "            if not isinstance(uid, str) or not uid or uid in self.units:\n                raise InvalidRecord(\"open needs a new unit id\")", "            pass"),
 "clear_halt is kernel-scope": ("mxm/kernel.py", "            if uid is not None:\n                raise InvalidRecord(\"clear_halt is kernel-scope\")", "            pass"),
 "anchor verification": ("mxm/eventlog.py", "        result = audit_chain.verify(self.path, anchor=anchor, check_legacy=False)", "        result = audit_chain.verify(self.path, anchor=None, check_legacy=False)"),
 "port halt check": ("mxm/kernel.py", "            stopped = self._stopped(unit_id)\n            if stopped:\n                return stopped", "            pass"),
 "NEW effects derived from the action": ("mxm/kernel.py", "        if effects != expected:", "        if False:"),
 "NEW decision kinds per action type": ("mxm/kernel.py", "        if outcome not in EFFECTING.get(act_type, ()):\n            raise", "        if False:\n            raise"),
 "NEW small-order rejection in verify": ("mxm/ed25519.py", "    if a is None or r is None or _small_order(a) or _small_order(r):", "    if a is None or r is None:"),
 "NEW subgroup check": ("mxm/ed25519.py", " and _is_identity(_mul(L, point))", ""),
 "NEW trust registry key validation": ("mxm/authz.py", "not ed25519.valid_public_key(public)", "len(public) != 32"),
 "NEW signing value domain": ("mxm/authz.py", "    _in_domain(obj)\n", ""),
 "NEW evidence answers an awaiting act": ("mxm/kernel.py", "self._awaiting.get(act_seq) != (uid, kind)", "False"),
 "NEW evidence written by the kernel": ("mxm/kernel.py", "            if rec.get(\"actor\") != \"kernel\" or self._awaiting", "            if self._awaiting"),
 "NEW halt written by the kernel": ("mxm/kernel.py", "            if rec.get(\"actor\") != \"kernel\" or not isinstance(p.get(\"reason\"), str):", "            if not isinstance(p.get(\"reason\"), str):"),
 "NEW lagging anchor moved forward": ("mxm/kernel.py", "                self.log.write_anchor(records[-1])", "                pass"),
 "NEW deleted anchor is a finding": ("mxm/eventlog.py", "        if self.anchor_path is not None and anchor is None and not problem and records:", "        if False:"),
 "NEW opening resolved before signing": ("mxm/kernel.py", "scope or self.constitution.mission.get(\"scope\", \"\")", "scope"),
 "NEW waiver needs a rationale on replay": ("mxm/kernel.py", "            if not (action.get(\"note\") or \"\").strip():\n                raise InvalidRecord(\"waiver without a rationale\")", "            pass"),
 "NEW7 unsigned principal record only as unverified denial": ("mxm/kernel.py", "        elif actor in PRINCIPALS:\n            # The one unsigned", "        elif False:\n            # The one unsigned"),
 "NEW7 recorded principal matches the key": ("mxm/kernel.py", "            if p.get(\"principal\") != principal:", "            if False:"),
 "NEW7 assistant records name no principal": ("mxm/kernel.py", "        elif p.get(\"principal\") is not None:", "        elif False:"),
 "NEW7 closing outcome validated": ("mxm/kernel.py", "            if outcome not in OUTCOMES or (outcome == \"failed\") != (\"error\" in p):", "            if False:"),
 "NEW7 orphaned obligation closed as unknown": ("mxm/kernel.py", "            self._evidence(unit_id, kind, {\"act_seq\": act_seq, \"outcome\": \"unknown\"})", "            pass"),
 "NEW7 skipped effect closed as not_executed": ("mxm/kernel.py", "                self._evidence(owed[0], owed[1], {\"act_seq\": rec[\"seq\"], \"outcome\": \"not_executed\"})", "                pass"),
 "NEW7 evidence failure halts the port": ("mxm/kernel.py", "        if err:\n            return \"halt\", \"evidence_unwritable\"", "        if False:\n            return \"halt\", \"evidence_unwritable\""),
 "NEW7 evidence failure stops the kernel": ("mxm/kernel.py", "            self._fatal = {\"reason\": \"evidence_unwritable\", \"detail\": err}", "            pass"),
}
missed = []
for name, (rel, old, new) in M.items():
    tmp = pathlib.Path("/tmp/mxk-mut"); shutil.rmtree(tmp, ignore_errors=True); shutil.copytree(src, tmp, ignore=shutil.ignore_patterns("__pycache__"))
    f = tmp / rel; s = f.read_text()
    if old not in s: print("ANCHOR NOT FOUND", name); missed.append(name); continue
    f.write_text(s.replace(old, new, 1))
    r = subprocess.run(["python3","-m","pytest","-q","-p","no:cacheprovider","-x",str(tmp/"tests")], capture_output=True, text=True)
    if not r.returncode: missed.append(name)
    print(("CAUGHT " if r.returncode else "MISSED ") + name)
shutil.rmtree("/tmp/mxk-mut", ignore_errors=True)
print(f"\n{len(M)-len(missed)}/{len(M)} caught; missed: {missed}")
