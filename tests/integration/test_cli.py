from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tarfile
from pathlib import Path

from conftest import PLUGIN_ROOT

CLI = PLUGIN_ROOT / "scripts" / "cmtk.py"


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        check=False,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )


def test_cli_inspect_emits_canonical_json(workspace_factory, tmp_path: Path):
    workspace = workspace_factory("source-carla-to-ue427")
    config = tmp_path / "workspace.json"
    config.write_text(json.dumps(workspace), encoding="utf-8")
    result = _run("inspect", "--route", "source-carla-to-ue427", "--config", str(config))
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "PASS"
    assert payload["route"] == "source-carla-to-ue427"


def test_cli_plan_and_verify_detect_workspace_staleness(workspace_factory, tmp_path: Path):
    workspace = workspace_factory("source-carla-to-package-carla")
    config = tmp_path / "workspace.json"
    plan = Path(workspace["execution"]["artifact_root"]) / "route-plan.json"
    config.write_text(json.dumps(workspace), encoding="utf-8")
    created = _run(
        "plan",
        "--route",
        "source-carla-to-package-carla",
        "--config",
        str(config),
        "--output",
        str(plan),
    )
    assert created.returncode == 0, created.stderr
    payload = json.loads(created.stdout)
    workspace["map"]["name"] = "ChangedMap"
    config.write_text(json.dumps(workspace), encoding="utf-8")
    verified = _run(
        "verify-plan", "--config", str(config), "--plan", str(plan), "--plan-sha256", payload["plan_sha256"]
    )
    assert verified.returncode == 2
    error = json.loads(verified.stdout)
    assert error["reason_code"] == "PLAN-STALE"


def test_cli_wrong_execution_context_fails_fast(workspace_factory, tmp_path: Path):
    workspace = workspace_factory("roadrunner-to-source-carla")
    config = tmp_path / "workspace.json"
    config.write_text(json.dumps(workspace), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(CLI), "inspect", "--route", "roadrunner-to-source-carla", "--config", str(config)],
        check=False,
        capture_output=True,
        text=True,
        env={
            **os.environ,
            "CMTK_EXECUTION_CONTEXT": "ue427-unreal-python",
            "PYTHONDONTWRITEBYTECODE": "1",
        },
    )
    assert result.returncode == 2
    payload = json.loads(result.stdout)
    assert payload["reason_code"] == "ENV-EXECUTION-CONTEXT-MISMATCH"


def test_cli_validate_reports_unreal_checks_as_not_run(workspace_factory, tmp_path: Path):
    workspace = workspace_factory("source-carla-to-ue427")
    config = tmp_path / "workspace.json"
    config.write_text(json.dumps(workspace), encoding="utf-8")
    result = _run("validate", "--route", "source-carla-to-ue427", "--config", str(config))
    assert result.returncode == 3, result.stderr
    payload = json.loads(result.stdout)
    assert payload["overall_status"] == "NOT_RUN"
    assert payload["evidence_level"] == "L1_LOGIC"
    assert "cold-copy dependency allowlist" in payload["not_run_checks"]


def test_cli_malformed_workspace_fails_with_structured_error(tmp_path: Path):
    config = tmp_path / "workspace.json"
    config.write_text("{}\n", encoding="utf-8")
    result = _run("inspect", "--route", "roadrunner-to-source-carla", "--config", str(config))
    assert result.returncode == 2
    assert result.stderr == ""
    payload = json.loads(result.stdout)
    assert payload["status"] == "BLOCKED"
    assert payload["reason_code"] == "WORKSPACE-INVALID"
    assert "missing" in payload["details"]


def test_cli_blocked_inspection_and_plan_do_not_signal_progress(workspace_factory, tmp_path: Path):
    workspace = workspace_factory("roadrunner-to-source-carla")
    (Path(workspace["input"]["root"]) / "ExampleMap.udatasmith").unlink()
    config = tmp_path / "workspace.json"
    config.write_text(json.dumps(workspace), encoding="utf-8")

    inspected = _run("inspect", "--route", "roadrunner-to-source-carla", "--config", str(config))
    assert inspected.returncode == 2
    inspection = json.loads(inspected.stdout)
    assert inspection["status"] == "BLOCKED"
    assert inspection["next_allowed_stages"] == []

    planned = _run("plan", "--route", "roadrunner-to-source-carla", "--config", str(config))
    assert planned.returncode == 2
    plan = json.loads(planned.stdout)
    assert "RR-EXPORT-MEMBER-MISSING" in plan["blocked_reasons"]


def test_verify_plan_rejects_a_blocked_plan(workspace_factory, tmp_path: Path):
    workspace = workspace_factory("roadrunner-to-source-carla")
    (Path(workspace["input"]["root"]) / "ExampleMap.udatasmith").unlink()
    config = tmp_path / "workspace.json"
    plan_path = Path(workspace["execution"]["artifact_root"]) / "blocked-plan.json"
    config.write_text(json.dumps(workspace), encoding="utf-8")
    created = _run(
        "plan",
        "--route",
        "roadrunner-to-source-carla",
        "--config",
        str(config),
        "--output",
        str(plan_path),
    )
    plan = json.loads(created.stdout)
    verified = _run(
        "verify-plan",
        "--config",
        str(config),
        "--plan",
        str(plan_path),
        "--plan-sha256",
        plan["plan_sha256"],
    )
    assert verified.returncode == 2
    assert json.loads(verified.stdout)["reason_code"] == "PLAN-BLOCKED"


def test_plan_output_must_stay_inside_workspace_allowed_roots(workspace_factory, tmp_path: Path):
    workspace = workspace_factory("roadrunner-to-source-carla")
    outside_root = tmp_path / "outside-artifacts"
    outside_root.mkdir()
    workspace["execution"]["artifact_root"] = str(outside_root)
    config = tmp_path / "workspace.json"
    output = outside_root / "route-plan.json"
    config.write_text(json.dumps(workspace), encoding="utf-8")
    result = _run(
        "plan",
        "--route",
        "roadrunner-to-source-carla",
        "--config",
        str(config),
        "--output",
        str(output),
    )
    assert result.returncode == 2
    assert json.loads(result.stdout)["reason_code"] == "PATH-OUTSIDE-ALLOWED-ROOT"
    assert not output.exists()


def test_plan_refuses_to_overwrite_existing_artifact(workspace_factory, tmp_path: Path):
    workspace = workspace_factory("roadrunner-to-source-carla")
    config = tmp_path / "workspace.json"
    output = Path(workspace["execution"]["artifact_root"]) / "route-plan.json"
    output.write_text("do-not-overwrite\n", encoding="utf-8")
    config.write_text(json.dumps(workspace), encoding="utf-8")
    result = _run(
        "plan",
        "--route",
        "roadrunner-to-source-carla",
        "--config",
        str(config),
        "--output",
        str(output),
    )
    assert result.returncode == 2
    assert json.loads(result.stdout)["reason_code"] == "OUTPUT-TARGET-EXISTS"
    assert output.read_text(encoding="utf-8") == "do-not-overwrite\n"


def test_performance_output_requires_an_allowed_root(tmp_path: Path):
    snapshot = {
        "conditions": {"vsync": False, "fps_cap": 0},
        "metrics": {"median_frame_ms": 20.0, "p95_frame_ms": 25.0},
        "protected": {
            "lod0_sha256": "a",
            "material_slots_sha256": "b",
            "transforms_sha256": "c",
            "collision_sha256": "d",
            "xodr_sha256": "e",
        },
    }
    baseline = tmp_path / "baseline.json"
    candidate = tmp_path / "candidate.json"
    output = tmp_path / "result.json"
    baseline.write_text(json.dumps(snapshot), encoding="utf-8")
    snapshot["metrics"]["median_frame_ms"] = 15.0
    snapshot["metrics"]["p95_frame_ms"] = 20.0
    candidate.write_text(json.dumps(snapshot), encoding="utf-8")
    result = _run(
        "compare-performance",
        "--baseline",
        str(baseline),
        "--candidate",
        str(candidate),
        "--output",
        str(output),
    )
    assert result.returncode == 2
    assert json.loads(result.stdout)["reason_code"] == "OUTPUT-ALLOWED-ROOT-REQUIRED"
    assert not output.exists()


def test_malformed_performance_input_returns_structured_error(tmp_path: Path):
    baseline = tmp_path / "baseline.json"
    candidate = tmp_path / "candidate.json"
    baseline.write_text("[]\n", encoding="utf-8")
    candidate.write_text("{}\n", encoding="utf-8")
    result = _run(
        "compare-performance",
        "--baseline",
        str(baseline),
        "--candidate",
        str(candidate),
        "--allowed-root",
        str(tmp_path),
    )
    assert result.returncode == 2
    assert result.stderr == ""
    assert json.loads(result.stdout)["reason_code"] == "PERF-INPUT-INVALID"


def test_archive_cli_requires_explicit_allowed_root(tmp_path: Path):
    archive = tmp_path / "package.tar"
    with tarfile.open(archive, "w"):
        pass
    result = _run("archive-audit", "--archive", str(archive))
    assert result.returncode == 2
    assert json.loads(result.stdout)["reason_code"] == "ARCHIVE-ALLOWED-ROOT-REQUIRED"


def test_source_unreal_adapter_records_stage_bound_evidence(workspace_factory, tmp_path: Path):
    workspace = workspace_factory("source-carla-to-ue427")
    artifact_root = Path(workspace["execution"]["artifact_root"])
    config = tmp_path / "workspace.json"
    plan_path = artifact_root / "route-plan.json"
    config.write_text(json.dumps(workspace), encoding="utf-8")
    planned = _run(
        "plan",
        "--route",
        "source-carla-to-ue427",
        "--config",
        str(config),
        "--output",
        str(plan_path),
    )
    assert planned.returncode == 0, planned.stdout
    plan = json.loads(planned.stdout)

    inventory = artifact_root / "source-asset-inventory.json"
    inventory.write_text('{"assets":["anonymous-road"]}\n', encoding="utf-8")
    inventory_sha256 = hashlib.sha256(inventory.read_bytes()).hexdigest()
    receipt = {
        "schema_version": "1.0.0",
        "run_id": "anonymous-source-baseline",
        "route": "source-carla-to-ue427",
        "stage": "SRC2UE427.BASELINE",
        "execution_context": "source-unreal-python",
        "plan_sha256": plan["plan_sha256"],
        "recorded_at": "2026-08-28T00:00:00Z",
        "environment": {
            "platform": "linux-x86_64",
            "source_carla_version": "0.9.16",
            "source_ue_version": "4.26.2-carla-fork",
            "runtime_engine_version": "4.26.2-fixture",
        },
        "operation": {
            "collector": "cmtk-source-unreal",
            "mode": "AUDIT",
        },
        "inputs": [],
        "actions": ["Audited the source Asset Registry."],
        "changes": [],
        "checks": [
            {
                "check_id": "source_asset_inventory_complete",
                "status": "PASS",
                "evidence_type": "deterministic-output",
                "summary": "The anonymous source asset inventory is complete.",
                "observations": [
                    {"name": "acceptance", "value": True, "source": "source-unreal-fixture"},
                    {"name": "asset_count", "value": 1, "source": "source-unreal-fixture"},
                ],
            }
        ],
        "metrics": [],
        "artifacts": [
            {
                "local_path": str(inventory),
                "public_path": "evidence/anonymous-source-baseline/support/source-asset-inventory.json",
                "sha256": inventory_sha256,
                "kind": "supporting",
            }
        ],
        "rollback": {"status": "NOT_APPLICABLE", "steps": []},
    }
    receipt_path = artifact_root / "source-baseline-receipt.json"
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    sensitive_terms = artifact_root / "private-literals.txt"
    sensitive_terms.write_text("private-fixture-term\n", encoding="utf-8")
    fake_module_root = tmp_path / "fake-source-unreal"
    fake_module_root.mkdir()
    (fake_module_root / "unreal.py").write_text(
        "class SystemLibrary:\n"
        "    @staticmethod\n"
        "    def get_engine_version():\n"
        "        return '4.26.2-fixture'\n",
        encoding="utf-8",
    )
    output_dir = artifact_root / "source-baseline-evidence"
    result = subprocess.run(
        [
            sys.executable,
            str(CLI),
            "record-stage-evidence",
            "--config",
            str(config),
            "--plan",
            str(plan_path),
            "--plan-sha256",
            plan["plan_sha256"],
            "--receipt",
            str(receipt_path),
            "--output-dir",
            str(output_dir),
            "--evidence-prefix",
            "evidence/anonymous-source-baseline/stages/baseline",
            "--sensitive-terms",
            str(sensitive_terms),
        ],
        check=False,
        capture_output=True,
        text=True,
        env={
            **os.environ,
            "CMTK_EXECUTION_CONTEXT": "source-unreal-python",
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONPATH": os.pathsep.join(
                [str(fake_module_root), os.environ.get("PYTHONPATH", "")]
            ),
        },
    )
    assert result.returncode == 0, result.stdout
    stage = json.loads(result.stdout)
    assert stage["stage"] == "SRC2UE427.BASELINE"
    assert stage["execution_context"] == "source-unreal-python"
    assert stage["status"] == "PASS"
    assert stage["checks"][0]["evidence"] == [
        "evidence/anonymous-source-baseline/stages/baseline/checks/source_asset_inventory_complete.json"
    ]
    assert (output_dir / "stage-result.json").is_file()
    assert (output_dir / "checks" / "source_asset_inventory_complete.json").is_file()
