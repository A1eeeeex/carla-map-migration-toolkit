from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from conftest import REPO_ROOT

DEMO = REPO_ROOT / "demo" / "quickstart" / "run_demo.py"


def _run(workspace_root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(DEMO), "--workspace-root", str(workspace_root)],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )


def test_quickstart_proves_host_plan_and_expected_safe_stop(tmp_path: Path):
    workspace_root = tmp_path / "quickstart"
    workspace_root.mkdir()

    result = _run(workspace_root)

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["demo_status"] == "PASS"
    assert payload["evidence_level"] == "L1_LOGIC"
    assert payload["inspection_status"] == "PASS"
    assert payload["plan_blocked_reasons"] == []
    assert payload["plan_verification_status"] == "PASS"
    assert payload["route_validation_status"] == "NOT_RUN"
    assert payload["expected_safe_stop"] is True

    plan = json.loads((workspace_root / "artifacts" / "route-plan.json").read_text(encoding="utf-8"))
    validation = json.loads(
        (workspace_root / "artifacts" / "validation-report.json").read_text(encoding="utf-8")
    )
    assert plan["plan_sha256"] == payload["plan_sha256"]
    assert validation["overall_status"] == "NOT_RUN"
    assert (workspace_root / "export" / "AnonymousDemo.udatasmith").is_file()
    assert (workspace_root / "export" / "AnonymousDemo.xodr").is_file()
    assert not any(path.suffix.lower() in {".uasset", ".umap", ".uexp", ".ubulk"} for path in workspace_root.rglob("*"))


def test_quickstart_refuses_to_write_inside_repository():
    unsafe_root = REPO_ROOT / "demo" / "quickstart" / "must-not-be-created"

    result = _run(unsafe_root)

    assert result.returncode == 2
    assert json.loads(result.stdout)["demo_status"] == "BLOCKED"
    assert not unsafe_root.exists()


def test_quickstart_refuses_a_symlinked_workspace(tmp_path: Path):
    target = tmp_path / "target"
    target.mkdir()
    workspace_link = tmp_path / "workspace-link"
    workspace_link.symlink_to(target, target_is_directory=True)

    result = _run(workspace_link)

    assert result.returncode == 2
    assert json.loads(result.stdout)["demo_status"] == "BLOCKED"
    assert list(target.iterdir()) == []
