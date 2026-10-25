"""Release and vendoring contract (ADR-MXK-0001): build, verify, install, and the stdlib runner."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]


def load(name):
    spec = importlib.util.spec_from_file_location(f"mxk_{name}", HERE.parent / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


release = load("release")
conformance = load("conformance")


@pytest.fixture
def built(tmp_path):
    out = tmp_path / "rel"
    manifest = release.build(REPO, "0.0.0-test", out)
    return out, manifest


def test_build_pins_every_file_and_the_tree(built):
    out, manifest = built
    assert manifest["files"] and all(len(d) == 64 for d in manifest["files"].values())
    assert manifest["aggregate_sha256"] == release.aggregate(manifest["files"])
    assert any(p.startswith("05-mxm-construct/means/enforcement/mxm/") for p in manifest["files"])
    assert "05-mxm-construct/means/release/release.py" in manifest["files"]
    assert json.loads((out / release.MANIFEST).read_text())["version"] == "0.0.0-test"


def test_verify_passes_a_clean_release_offline_with_conformance(built):
    out, manifest = built
    result = release.verify(out, expect=manifest["aggregate_sha256"])
    assert result["ok"], result["problems"]


@pytest.mark.parametrize("tamper", ["modify", "delete", "add", "pin"])
def test_verify_fails_closed_on_any_tamper(built, tamper):
    out, manifest = built
    target = out / "05-mxm-construct/means/enforcement/mxm/kernel.py"
    expect = manifest["aggregate_sha256"]
    if tamper == "modify":
        target.write_text(target.read_text() + "\n# drift\n")
    elif tamper == "delete":
        target.unlink()
    elif tamper == "add":
        (out / "05-mxm-construct/means/enforcement/mxm/extra.py").write_text("x = 1\n")
    else:
        expect = "0" * 64
    result = release.verify(out, expect=expect, conformance=False)
    assert not result["ok"] and result["problems"]


def test_containment_refuses_an_external_import(built):
    out, manifest = built
    rel = "05-mxm-construct/means/enforcement/mxm/kernel.py"
    path = out / rel
    path.write_text("import requests\n" + path.read_text())
    manifest["files"][rel] = release._sha256(path)
    problems = release.check_containment(out, manifest)
    assert any("external import 'requests'" in p for p in problems)


def test_install_vendors_writes_a_lock_and_refuses_a_wrong_pin(built, tmp_path):
    out, manifest = built
    with pytest.raises(SystemExit):
        release.install(out, tmp_path / "vendor-bad", expect="0" * 64)
    into = tmp_path / "harness" / "vendor" / "mxm-kernel"
    release.install(out, into, expect=manifest["aggregate_sha256"])
    lock = json.loads((into / release.LOCK).read_text())
    assert lock["aggregate_sha256"] == manifest["aggregate_sha256"]
    assert release.verify(into, expect=manifest["aggregate_sha256"], conformance=False)["ok"]


def _suite(tmp_path, body):
    suite = tmp_path / "suite"
    suite.mkdir()
    (suite / "test_probe.py").write_text("import pytest\n" + body)
    return suite


def test_stdlib_runner_detects_failure_and_strict_xpass(tmp_path):
    suite = _suite(tmp_path, (
        "def test_ok():\n    assert True\n"
        "def test_broken():\n    assert 1 == 2\n"
        "@pytest.mark.xfail(strict=True, reason='gap')\n"
        "def test_gap_closed():\n    assert True\n"))
    result = conformance.run_suite(suite)
    assert (result["passed"], result["failed"], result["xpassed_strict"]) == (1, 1, 1)


def test_stdlib_runner_supports_fixtures_parametrize_raises(tmp_path):
    suite = _suite(tmp_path, (
        "@pytest.fixture\n"
        "def base(tmp_path):\n    return tmp_path\n"
        "@pytest.mark.parametrize('n', [1, 2, 3])\n"
        "def test_param(base, n):\n    assert base.is_dir() and n > 0\n"
        "def test_raises():\n"
        "    with pytest.raises(ValueError, match='bad'):\n        raise ValueError('bad input')\n"))
    result = conformance.run_suite(suite)
    assert (result["passed"], result["failed"]) == (4, 0)


def test_stdlib_runner_refuses_unsupported_features(tmp_path):
    suite = _suite(tmp_path, (
        "@pytest.mark.skipif(True, reason='x')\n"
        "def test_x():\n    pass\n"))
    with pytest.raises(NotImplementedError):
        conformance.run_suite(suite)


def test_stdlib_runner_matches_pytest_on_the_kernel_suite():
    suite = REPO / "05-mxm-construct/means/enforcement/tests"
    result = conformance.run_suite(suite)
    assert (result["passed"], result["xfailed"], result["failed"], result["xpassed_strict"]) == (161, 3, 0, 0)


def test_cli_verify_exit_codes(built, tmp_path):
    out, manifest = built
    ok = subprocess.run([sys.executable, str(out / "05-mxm-construct/means/release/release.py"), "verify",
                         str(out), "--expect", manifest["aggregate_sha256"]], capture_output=True, text=True)
    assert ok.returncode == 0, ok.stdout + ok.stderr
    bad = subprocess.run([sys.executable, str(out / "05-mxm-construct/means/release/release.py"), "verify",
                          str(out), "--expect", "0" * 64, "--no-conformance"], capture_output=True, text=True)
    assert bad.returncode == 1
