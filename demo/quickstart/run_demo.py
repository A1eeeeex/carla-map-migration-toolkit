#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

ROUTE = "roadrunner-to-source-carla"
REPO_ROOT = Path(__file__).resolve().parents[2]
CLI = REPO_ROOT / "plugins" / "carla-map-migration-toolkit" / "scripts" / "cmtk.py"


class DemoError(RuntimeError):
    pass


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _prepare_workspace_root(raw_path: str) -> Path:
    requested = Path(raw_path)
    if not requested.is_absolute():
        raise DemoError("--workspace-root must be an absolute path to a dedicated empty directory.")
    if any(path.is_symlink() for path in (requested, *requested.parents) if path.exists()):
        raise DemoError("The demo workspace path must not contain a symbolic link.")

    root = requested.resolve(strict=False)
    home = Path.home().resolve(strict=False)
    if (
        root == Path(root.anchor)
        or root == home
        or root.is_relative_to(home)
        or root == REPO_ROOT
        or root.is_relative_to(REPO_ROOT)
    ):
        raise DemoError("The demo workspace must not be a filesystem root, home directory, or repository path.")
    if root.exists():
        if not root.is_dir() or any(root.iterdir()):
            raise DemoError("The demo workspace must be an empty directory.")
    else:
        if not root.parent.is_dir():
            raise DemoError("The demo workspace parent directory must already exist.")
        root.mkdir()
    return root


def _create_fixture(root: Path) -> Path:
    export_root = root / "export"
    source_root = root / "source-carla"
    backup_root = root / "backups"
    artifact_root = root / "artifacts"
    for path in (export_root, source_root, backup_root, artifact_root):
        path.mkdir()

    datasmith_path = export_root / "AnonymousDemo.udatasmith"
    datasmith_path.write_text(
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        "<DatasmithUnrealScene version=\"synthetic-host-fixture\">\n"
        "  <Host>cmtk-quickstart</Host>\n"
        "</DatasmithUnrealScene>\n",
        encoding="utf-8",
    )
    xodr_path = export_root / "AnonymousDemo.xodr"
    xodr_path.write_text(
        "<?xml version=\"1.0\" standalone=\"yes\"?>\n"
        "<OpenDRIVE>\n"
        "  <header revMajor=\"1\" revMinor=\"4\" name=\"AnonymousDemo\" version=\"1.00\"/>\n"
        "  <road name=\"SyntheticRoad\" length=\"10.0\" id=\"1\" junction=\"-1\">\n"
        "    <planView><geometry s=\"0\" x=\"0\" y=\"0\" hdg=\"0\" length=\"10\"><line/></geometry></planView>\n"
        "    <lanes><laneSection s=\"0\"><center>\n"
        "      <lane id=\"0\" type=\"none\" level=\"false\"/>\n"
        "    </center></laneSection></lanes>\n"
        "  </road>\n"
        "</OpenDRIVE>\n",
        encoding="utf-8",
    )

    workspace = {
        "schema_version": "1.0.0",
        "workspace_id": "anonymous-quickstart",
        "route": ROUTE,
        "map": {"id": "anonymous-demo", "name": "AnonymousDemo", "mode": "standard"},
        "input": {"profile": "roadrunner-datasmith", "root": str(export_root)},
        "source_carla": {
            "root": str(source_root),
            "version": "0.9.16",
            "branch": "anonymous-fixture",
            "commit": "0" * 40,
            "engine_version": "4.26.2-carla-fork",
            "platform": "linux-x86_64",
            "map_asset_path": "/Game/Carla/Maps/AnonymousDemo/AnonymousDemo",
            "xodr_path": str(xodr_path),
        },
        "execution": {
            "mode": "plan",
            "backup_root": str(backup_root),
            "artifact_root": str(artifact_root),
            "allow_replace_existing": False,
            "allowed_roots": [str(root)],
        },
        "performance": {"enabled": False, "profile": None},
    }
    config_path = root / "map-workspace.json"
    _write_json(config_path, workspace)
    return config_path


def _run_cli(*args: str, expected_returncode: int) -> dict[str, Any]:
    result = subprocess.run(
        [sys.executable, str(CLI), *args],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        env={
            **os.environ,
            "CMTK_EXECUTION_CONTEXT": "host-cpython",
            "PYTHONDONTWRITEBYTECODE": "1",
        },
    )
    if result.returncode != expected_returncode:
        raise DemoError(
            f"cmtk {' '.join(args[:1])} returned {result.returncode}; expected {expected_returncode}. "
            f"stdout={result.stdout.strip()!r} stderr={result.stderr.strip()!r}"
        )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise DemoError(f"cmtk {' '.join(args[:1])} did not return JSON.") from error
    if not isinstance(payload, dict):
        raise DemoError(f"cmtk {' '.join(args[:1])} returned a non-object JSON value.")
    return payload


def run_demo(workspace_root: str) -> dict[str, Any]:
    root = _prepare_workspace_root(workspace_root)
    config_path = _create_fixture(root)
    artifact_root = root / "artifacts"
    plan_path = artifact_root / "route-plan.json"
    validation_path = artifact_root / "validation-report.json"

    inspection = _run_cli("inspect", "--route", ROUTE, "--config", str(config_path), expected_returncode=0)
    plan = _run_cli(
        "plan",
        "--route",
        ROUTE,
        "--config",
        str(config_path),
        "--output",
        str(plan_path),
        expected_returncode=0,
    )
    plan_sha256 = plan.get("plan_sha256")
    if not isinstance(plan_sha256, str):
        raise DemoError("The generated route plan has no SHA-256 seal.")
    verified = _run_cli(
        "verify-plan",
        "--config",
        str(config_path),
        "--plan",
        str(plan_path),
        "--plan-sha256",
        plan_sha256,
        expected_returncode=0,
    )
    validation = _run_cli(
        "validate",
        "--route",
        ROUTE,
        "--config",
        str(config_path),
        "--output",
        str(validation_path),
        expected_returncode=3,
    )

    if inspection.get("status") != "PASS" or plan.get("blocked_reasons") != []:
        raise DemoError("The synthetic input did not produce an unblocked read-only plan.")
    if verified.get("status") != "PASS" or validation.get("overall_status") != "NOT_RUN":
        raise DemoError("The plan seal or expected runtime-validation safe stop did not hold.")

    return {
        "schema_version": "1.0.0",
        "demo_status": "PASS",
        "route": ROUTE,
        "evidence_level": "L1_LOGIC",
        "inspection_status": inspection["status"],
        "plan_blocked_reasons": plan["blocked_reasons"],
        "plan_sha256": plan_sha256,
        "plan_verification_status": verified["status"],
        "route_validation_status": validation["overall_status"],
        "expected_safe_stop": True,
        "workspace_root": str(root),
        "note": "This host-only synthetic demo does not claim an Unreal Editor or CARLA runtime migration.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the rights-safe CARLA Map Migration Toolkit quickstart.")
    parser.add_argument("--workspace-root", required=True)
    args = parser.parse_args()
    try:
        result = run_demo(args.workspace_root)
    except (DemoError, OSError) as error:
        print(json.dumps({"schema_version": "1.0.0", "demo_status": "BLOCKED", "message": str(error)}))
        raise SystemExit(2) from None
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
