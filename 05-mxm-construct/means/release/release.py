#!/usr/bin/env python3
"""MxM kernel release and vendoring contract (ADR-MXK-0001). Standard library only.

A *release* is a directory holding the paths named in release.json, plus
`release-manifest.json`, which pins every file by SHA-256 and pins the whole tree by an
aggregate hash. A harness *vendors* a release by copying it into its own tree and
recording the aggregate hash it expects. *Verification* runs offline and fails closed:

  1. integrity: every file matches its pin; nothing is missing or extra; the aggregate matches;
  2. containment: no Python file imports anything outside the standard library and the
     release itself (test files may also import `pytest`, which the conformance runner
     can supply);
  3. conformance: the shipped suites pass under the shipped stdlib runner.

    release.py build   --version V --out DIR          assemble a release from this repository
    release.py verify  DIR [--expect AGGREGATE]        verify a release or a vendored copy
    release.py install --from DIR --into DIR --expect AGGREGATE
                                                       vendor a verified release into a harness
"""

from __future__ import annotations

import argparse
import ast
import fnmatch
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

MANIFEST = "release-manifest.json"
LOCK = "mxm-kernel.lock.json"
CONFIG = Path(__file__).with_name("release.json")
CONFIG_REL = "05-mxm-construct/means/release/release.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _excluded(rel: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(part, pat) for part in Path(rel).parts for pat in patterns)


def collect(root: Path, config: dict) -> dict[str, str]:
    """Relative path -> sha256 for every file under the configured release paths."""
    files = {}
    for base in config["release_paths"]:
        for path in sorted((root / base).rglob("*")):
            rel = path.relative_to(root).as_posix()
            if path.is_file() and not _excluded(rel, config.get("exclude", [])):
                files[rel] = _sha256(path)
    return files


def aggregate(files: dict[str, str]) -> str:
    body = "".join(f"{digest}  {rel}\n" for rel, digest in sorted(files.items()))
    return hashlib.sha256(body.encode()).hexdigest()


def _source_commit(root: Path) -> str | None:
    try:
        out = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True,
                             text=True, timeout=10)
        return out.stdout.strip() or None if out.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def build(root: Path, version: str, out: Path) -> dict:
    config = json.loads((root / CONFIG_REL).read_text())
    if out.exists() and any(out.iterdir()):
        raise SystemExit(f"output directory not empty: {out}")
    files = collect(root, config)
    for rel in files:
        target = out / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(root / rel, target)
    manifest = {"name": config["name"], "version": version, "source_commit": _source_commit(root),
                "python_min": config["python_min"], "platform": config["platform"],
                "conformance_suites": config["conformance_suites"],
                "files": files, "aggregate_sha256": aggregate(files)}
    (out / MANIFEST).write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest


def check_integrity(tree: Path, manifest: dict) -> list[str]:
    problems = []
    listed = manifest.get("files", {})
    for rel, digest in listed.items():
        path = tree / rel
        if not path.is_file():
            problems.append(f"missing: {rel}")
        elif _sha256(path) != digest:
            problems.append(f"modified: {rel}")
    for path in tree.rglob("*"):
        rel = path.relative_to(tree).as_posix()
        if (path.is_file() and rel not in listed and rel not in (MANIFEST, LOCK)
                and not _excluded(rel, ["__pycache__", ".pytest_cache", "*.pyc"])):
            problems.append(f"extra: {rel}")
    if aggregate(listed) != manifest.get("aggregate_sha256"):
        problems.append("aggregate hash does not match the listed files")
    return problems


def check_containment(tree: Path, manifest: dict) -> list[str]:
    """Imports must resolve to the standard library or to modules shipped in the release."""
    stdlib = set(sys.stdlib_module_names)
    local = set()
    for rel in manifest.get("files", {}):
        p = Path(rel)
        if p.suffix == ".py":
            local.add(p.stem)
        local.update(part for part in p.parts[:-1])
    problems = []
    for rel in manifest.get("files", {}):
        if not rel.endswith(".py"):
            continue
        is_test = "tests" in Path(rel).parts
        for node in ast.walk(ast.parse((tree / rel).read_text(), filename=rel)):
            if isinstance(node, ast.Import):
                names = [a.name.split(".")[0] for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0:
                names = [(node.module or "").split(".")[0]]
            else:
                continue
            for name in names:
                if name in stdlib or name in local or (is_test and name == "pytest"):
                    continue
                problems.append(f"external import '{name}' in {rel}")
    return problems


def check_conformance(tree: Path, manifest: dict) -> list[str]:
    runner = tree / "05-mxm-construct/means/release/conformance.py"
    problems = []
    for suite in manifest.get("conformance_suites", []):
        # -I -S: isolated mode without site-packages, so conformance cannot lean on anything
        # installed outside the release (the air-gap condition), even when it is present.
        proc = subprocess.run([sys.executable, "-I", "-S", str(runner), "--stdlib", str(tree / suite)],
                              capture_output=True, text=True, timeout=600)
        if proc.returncode != 0:
            problems.append(f"conformance failed: {suite}\n{proc.stdout[-2000:]}{proc.stderr[-1000:]}")
    return problems


def verify(tree: Path, expect: str | None = None, conformance: bool = True) -> dict:
    manifest_path = tree / MANIFEST
    if not manifest_path.is_file():
        return {"ok": False, "problems": [f"no {MANIFEST} in {tree}"]}
    manifest = json.loads(manifest_path.read_text())
    problems = []
    if expect and manifest.get("aggregate_sha256") != expect:
        problems.append(f"pin mismatch: expected {expect}, release is {manifest.get('aggregate_sha256')}")
    problems += check_integrity(tree, manifest)
    problems += check_containment(tree, manifest) if not problems else []
    if conformance and not problems:
        problems += check_conformance(tree, manifest)
    return {"ok": not problems, "version": manifest.get("version"),
            "aggregate_sha256": manifest.get("aggregate_sha256"), "problems": problems}


def install(source: Path, into: Path, expect: str) -> dict:
    result = verify(source, expect=expect)
    if not result["ok"]:
        raise SystemExit("refusing to vendor an unverified release:\n  " + "\n  ".join(result["problems"]))
    if into.exists() and any(into.iterdir()):
        raise SystemExit(f"vendor directory not empty: {into} (remove the previous release first)")
    shutil.copytree(source, into, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache", "*.pyc"))
    installed = verify(into, expect=expect)
    if not installed["ok"]:
        raise SystemExit("vendored copy failed verification:\n  " + "\n  ".join(installed["problems"]))
    (into / LOCK).write_text(json.dumps({"name": "mxm-kernel", "version": installed["version"],
                                         "aggregate_sha256": expect}, indent=2) + "\n")
    return installed


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build"); b.add_argument("--version", required=True); b.add_argument("--out", type=Path, required=True)
    b.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[3])
    v = sub.add_parser("verify"); v.add_argument("tree", type=Path); v.add_argument("--expect")
    v.add_argument("--no-conformance", action="store_true")
    i = sub.add_parser("install"); i.add_argument("--from", dest="source", type=Path, required=True)
    i.add_argument("--into", type=Path, required=True); i.add_argument("--expect", required=True)
    args = ap.parse_args(argv)
    if args.cmd == "build":
        m = build(args.root, args.version, args.out)
        print(json.dumps({"version": m["version"], "files": len(m["files"]), "aggregate_sha256": m["aggregate_sha256"]}))
        return 0
    if args.cmd == "verify":
        r = verify(args.tree, args.expect, conformance=not args.no_conformance)
        print(json.dumps(r, indent=2))
        return 0 if r["ok"] else 1
    r = install(args.source, args.into, args.expect)
    print(json.dumps({"vendored": str(args.into), "version": r["version"], "aggregate_sha256": r["aggregate_sha256"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
