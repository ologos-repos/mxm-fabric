#!/usr/bin/env python3
"""Standard-library conformance runner for the MxM kernel (ADR-MXK-0001).

Air-gapped harnesses cannot be assumed to have pytest. This runner executes the kernel's
conformance suites with the standard library alone. It supplies a minimal stand-in for the
pytest features the suites use (fixtures, the `tmp_path` fixture, `mark.parametrize`,
strict `mark.xfail`, `raises`) and refuses anything else rather than guessing.

    conformance.py [--stdlib] SUITE_DIR [SUITE_DIR ...]

Without --stdlib, a real pytest is used when importable; with --stdlib (what release
verification uses), the stand-in is always used. The exit code is 0 only when every test
passed or failed as a declared strict xfail.
"""

from __future__ import annotations

import importlib.util
import inspect
import re
import shutil
import subprocess
import sys
import tempfile
import traceback
import types
from pathlib import Path


class _XFail:
    def __init__(self, reason="", strict=False):
        self.reason, self.strict = reason, strict


class _Param:
    def __init__(self, argnames, values):
        self.argnames = [a.strip() for a in argnames.split(",")] if isinstance(argnames, str) else list(argnames)
        self.values = list(values)


def _mark(fn, key, value):
    fn.__dict__.setdefault("_mxk_marks", []).append((key, value))
    return fn


class _Mark:
    def xfail(self, reason="", strict=False, **kw):
        if kw:
            raise NotImplementedError(f"xfail options not supported: {sorted(kw)}")
        return lambda fn: _mark(fn, "xfail", _XFail(reason, strict))

    def parametrize(self, argnames, values, **kw):
        if kw:
            raise NotImplementedError(f"parametrize options not supported: {sorted(kw)}")
        return lambda fn: _mark(fn, "param", _Param(argnames, values))

    def __getattr__(self, name):
        raise NotImplementedError(f"pytest.mark.{name} is not supported by the stdlib runner")


class _Raises:
    def __init__(self, exc, match=None):
        self.exc, self.match = exc, match

    def __enter__(self):
        return self

    def __exit__(self, etype, value, tb):
        if etype is None:
            raise AssertionError(f"DID NOT RAISE {self.exc}")
        if not issubclass(etype, self.exc):
            return False
        if self.match and not re.search(self.match, str(value)):
            raise AssertionError(f"pattern {self.match!r} not found in {str(value)!r}")
        return True


def _fixture(fn=None, **kw):
    if kw.get("scope") not in (None, "function"):
        raise NotImplementedError("only function-scoped fixtures are supported")
    def wrap(f):
        f._mxk_fixture = True
        return f
    return wrap(fn) if fn else wrap


def _stub_module() -> types.ModuleType:
    mod = types.ModuleType("pytest")
    mod.mark, mod.raises, mod.fixture = _Mark(), _Raises, _fixture
    mod.__mxk_stub__ = True
    return mod


def _resolve(name, fixtures, tmp, cache):
    if name in cache:
        return cache[name]
    if name == "tmp_path":
        value = Path(tempfile.mkdtemp(dir=tmp))
    elif name in fixtures:
        fn = fixtures[name]
        value = fn(**{a: _resolve(a, fixtures, tmp, cache) for a in inspect.signature(fn).parameters})
    else:
        raise NotImplementedError(f"unknown fixture '{name}'")
    cache[name] = value
    return value


def _cases(fn):
    marks = fn.__dict__.get("_mxk_marks", [])
    xfail = next((v for k, v in marks if k == "xfail"), None)
    params = [v for k, v in marks if k == "param"]
    if not params:
        return [({}, "", xfail)]
    if len(params) > 1:
        raise NotImplementedError("stacked parametrize is not supported")
    p = params[0]
    out = []
    for i, val in enumerate(p.values):
        vals = val if len(p.argnames) > 1 else (val,)
        out.append((dict(zip(p.argnames, vals)), f"[{i}]", xfail))
    return out


def run_suite(suite: Path) -> dict:
    previous = sys.modules.get("pytest")
    sys.modules["pytest"] = _stub_module()
    try:
        return _run(suite)
    finally:
        if previous is None:
            sys.modules.pop("pytest", None)
        else:
            sys.modules["pytest"] = previous


def _run(suite: Path) -> dict:
    counts = {"passed": 0, "failed": 0, "xfailed": 0, "xpassed_strict": 0}
    failures = []
    for path in sorted(suite.glob("test_*.py")):
        spec = importlib.util.spec_from_file_location(f"mxk_conf_{path.stem}", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        fixtures = {n: f for n, f in vars(module).items() if getattr(f, "_mxk_fixture", False)}
        for name, fn in vars(module).items():
            if not (name.startswith("test_") and callable(fn)):
                continue
            for bound, suffix, xfail in _cases(fn):
                tmp = tempfile.mkdtemp(prefix="mxk-conf-")
                try:
                    cache = dict(bound)
                    kwargs = {a: _resolve(a, fixtures, tmp, cache) for a in inspect.signature(fn).parameters}
                    fn(**kwargs)
                    outcome = "passed"
                except NotImplementedError:
                    raise
                except Exception:
                    outcome, err = "failed", traceback.format_exc(limit=3)
                finally:
                    shutil.rmtree(tmp, ignore_errors=True)
                test_id = f"{path.name}::{name}{suffix}"
                if xfail and outcome == "failed":
                    counts["xfailed"] += 1
                elif xfail and outcome == "passed":
                    if xfail.strict:
                        counts["xpassed_strict"] += 1
                        failures.append(f"{test_id}: XPASS(strict) {xfail.reason}")
                    else:
                        counts["passed"] += 1
                elif outcome == "passed":
                    counts["passed"] += 1
                else:
                    counts["failed"] += 1
                    failures.append(f"{test_id}\n{err}")
    return {"suite": str(suite), **counts, "failures": failures}


def main(argv=None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    stdlib = "--stdlib" in args
    suites = [Path(a) for a in args if a != "--stdlib"]
    if not suites:
        print(__doc__)
        return 2
    if not stdlib and importlib.util.find_spec("pytest") is not None:
        return subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", *map(str, suites)]).returncode
    ok = True
    for suite in suites:
        result = run_suite(suite)
        print(f"{result['suite']}: {result['passed']} passed, {result['xfailed']} xfailed, "
              f"{result['failed']} failed, {result['xpassed_strict']} xpassed(strict)")
        for failure in result["failures"]:
            print("  FAIL", failure)
        ok = ok and not result["failures"]
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
