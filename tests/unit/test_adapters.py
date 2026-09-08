from __future__ import annotations

import ast
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import cmtk.adapters.evidence as evidence_adapter
import pytest
from cmtk.adapters.evidence import record_stage_evidence
from cmtk.core.errors import CmtkError
from cmtk.routes.catalog import REQUIRED_CHECK_EVIDENCE_TYPES, REQUIRED_CHECK_STAGES
from cmtk.routes.inspection import inspect_workspace
from cmtk.routes.planning import build_plan
from conftest import PLUGIN_ROOT

CONTEXT_RECEIPT = PLUGIN_ROOT / "scripts" / "context_receipt.py"


def _plan(workspace: dict) -> dict:
    return build_plan(workspace, workspace["route"], inspect_workspace(workspace, workspace["route"]))


def _file_record(root: Path, name: str, public_path: str) -> dict:
    path = root / name
    path.write_text(json.dumps({"record": name}) + "\n", encoding="utf-8")
    return {
        "local_path": str(path),
        "public_path": public_path,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "kind": "supporting",
    }


def _environment(workspace: dict, context: str, runtime_version: str = "") -> dict:
    if context == "source-unreal-python":
        return {
            "platform": "linux-x86_64",
            "source_carla_version": workspace["source_carla"]["version"],
            "source_ue_version": workspace["source_carla"]["engine_version"],
            "runtime_engine_version": runtime_version,
        }
    if context == "ue427-unreal-python":
        return {
            "platform": "linux-x86_64",
            "target_ue_version": workspace["ue427"]["engine_version"],
            "runtime_engine_version": runtime_version,
        }
    if context == "carla-client-python":
        version = (
            workspace["package_carla"]["version"]
            if workspace["route"] == "source-carla-to-package-carla"
            else workspace["source_carla"]["version"]
        )
        return {
            "platform": "linux-x86_64",
            "carla_client_version": version,
            "carla_server_version": version,
        }
    return {
        "platform": "linux-x86_64",
        "source_carla_version": workspace["source_carla"]["version"],
        "target_carla_version": workspace["package_carla"]["version"],
    }


def _receipt(
    workspace: dict,
    plan: dict,
    *,
    stage: str,
    context: str,
    check_id: str,
    evidence_type: str,
    observations: list[dict] | None = None,
    runtime_version: str = "",
    write_stage: bool = False,
    complete_stage: bool = True,
) -> dict:
    root = Path(workspace["execution"]["artifact_root"])
    artifact = _file_record(root, f"{check_id}.json", f"evidence/anonymous/support/{check_id}.json")
    operation = {"collector": f"cmtk-{context}", "mode": "APPLY_PLAN" if write_stage else "AUDIT"}
    rollback: dict = {"status": "NOT_APPLICABLE", "steps": []}
    changes: list[str] = []
    if context == "shell-build":
        operation.update({"command_sha256": "c" * 64, "return_code": 0})
    if write_stage:
        backup = _file_record(root, f"{check_id}-backup.json", f"evidence/anonymous/support/{check_id}-backup.json")
        rollback = {
            "status": "READY",
            "steps": ["Restore only entries listed by the anonymous backup manifest."],
            "backup_manifest": backup,
        }
        changes = ["Applied the sealed anonymous stage plan."]
    checks = [
        {
            "check_id": check_id,
            "status": "PASS",
            "evidence_type": evidence_type,
            "summary": "The anonymous contract observation passed.",
            "observations": observations
            or [{"name": "acceptance", "value": True, "source": "anonymous-adapter"}],
        }
    ]
    if complete_stage:
        for required_id, stages in REQUIRED_CHECK_STAGES[workspace["route"]].items():
            if stage not in stages or required_id == check_id:
                continue
            checks.append(
                {
                    "check_id": required_id,
                    "status": "PASS",
                    "evidence_type": REQUIRED_CHECK_EVIDENCE_TYPES[workspace["route"]][required_id],
                    "summary": "The anonymous required stage observation passed.",
                    "observations": [
                        {"name": "acceptance", "value": True, "source": "anonymous-adapter"}
                    ],
                }
            )
    return {
        "schema_version": "1.0.0",
        "run_id": f"anonymous-{check_id}",
        "route": workspace["route"],
        "stage": stage,
        "execution_context": context,
        "plan_sha256": plan["plan_sha256"],
        "recorded_at": "2026-08-28T00:00:00Z",
        "environment": _environment(workspace, context, runtime_version),
        "operation": operation,
        "inputs": [],
        "actions": ["Collected an anonymous execution-context receipt."],
        "changes": changes,
        "checks": checks,
        "metrics": [],
        "artifacts": [artifact],
        "rollback": rollback,
    }


def _record(workspace: dict, plan: dict, receipt: dict, name: str) -> dict:
    root = Path(workspace["execution"]["artifact_root"])
    terms = root / f"{name}-sensitive-terms.txt"
    terms.write_text("private-anonymous-term\n", encoding="utf-8")
    return record_stage_evidence(
        workspace,
        plan,
        receipt,
        output_dir=str(root / f"{name}-evidence"),
        evidence_prefix=f"evidence/anonymous/stages/{name}",
        sensitive_terms_path=str(terms),
    )


def _fake_unreal(monkeypatch, version: str) -> None:
    system_library = SimpleNamespace(get_engine_version=lambda: version)
    monkeypatch.setitem(sys.modules, "unreal", SimpleNamespace(SystemLibrary=system_library))


def test_roadrunner_source_unreal_receipt_uses_post_import_editor_stage(
    workspace_factory, monkeypatch
):
    workspace = workspace_factory("roadrunner-to-source-carla")
    plan = _plan(workspace)
    runtime = "4.26.2-anonymous"
    _fake_unreal(monkeypatch, runtime)
    monkeypatch.setenv("CMTK_EXECUTION_CONTEXT", "source-unreal-python")
    receipt = _receipt(
        workspace,
        plan,
        stage="RR2SRC.POST_IMPORT_AUDIT",
        context="source-unreal-python",
        check_id="required_materials_valid",
        evidence_type="editor-audit",
        runtime_version=runtime,
    )

    result = _record(workspace, plan, receipt, "rr-post-import")

    assert result["status"] == "PASS"
    assert result["execution_context"] == "source-unreal-python"


def test_ue427_receipt_requires_live_target_unreal_boundary(workspace_factory, monkeypatch):
    workspace = workspace_factory("source-carla-to-ue427")
    plan = _plan(workspace)
    runtime = "4.27.2-anonymous"
    _fake_unreal(monkeypatch, runtime)
    monkeypatch.setenv("CMTK_EXECUTION_CONTEXT", "ue427-unreal-python")
    receipt = _receipt(
        workspace,
        plan,
        stage="SRC2UE427.TARGET_VALIDATE",
        context="ue427-unreal-python",
        check_id="target_reopen",
        evidence_type="editor-audit",
        runtime_version=runtime,
    )

    result = _record(workspace, plan, receipt, "ue427-target")

    assert result["status"] == "PASS"
    assert result["execution_context"] == "ue427-unreal-python"


def test_carla_receipt_requires_matching_client_and_server_versions(workspace_factory, monkeypatch):
    workspace = workspace_factory("source-carla-to-package-carla")
    plan = _plan(workspace)
    monkeypatch.setitem(sys.modules, "carla", SimpleNamespace(Client=object))
    monkeypatch.setenv("CMTK_EXECUTION_CONTEXT", "carla-client-python")
    receipt = _receipt(
        workspace,
        plan,
        stage="SRC2PKG.RUNTIME_VALIDATE",
        context="carla-client-python",
        check_id="dynamic_smoke",
        evidence_type="runtime-measurement",
    )

    result = _record(workspace, plan, receipt, "package-runtime")

    assert result["status"] == "PASS"
    assert result["execution_context"] == "carla-client-python"
    assert {item["confidence"] for item in result["checks"]} == {"sampled"}


def test_shell_build_receipt_requires_command_backup_and_rollback(workspace_factory, monkeypatch):
    workspace = workspace_factory("source-carla-to-package-carla")
    plan = _plan(workspace)
    monkeypatch.setenv("CMTK_EXECUTION_CONTEXT", "shell-build")
    receipt = _receipt(
        workspace,
        plan,
        stage="SRC2PKG.BUILD",
        context="shell-build",
        check_id="package_artifact_hashed",
        evidence_type="deterministic-output",
        write_stage=True,
    )

    result = _record(workspace, plan, receipt, "package-build")

    assert result["status"] == "PASS"
    assert result["rollback"]["status"] == "READY"
    assert "local_path" not in json.dumps(result)


@pytest.mark.parametrize(
    ("route", "stage", "context", "runtime"),
    [
        ("roadrunner-to-source-carla", "RR2SRC.REPAIR", "source-unreal-python", "4.26.2-anonymous"),
        ("source-carla-to-package-carla", "SRC2PKG.REPAIR", "source-unreal-python", "4.26.2-anonymous"),
        ("source-carla-to-ue427", "SRC2UE427.REPAIR_MATERIALS", "ue427-unreal-python", "4.27.2-anonymous"),
    ],
)
def test_all_three_routes_record_complete_repair_contracts(
    workspace_factory, monkeypatch, route, stage, context, runtime
):
    workspace = workspace_factory(route)
    plan = _plan(workspace)
    _fake_unreal(monkeypatch, runtime)
    monkeypatch.setenv("CMTK_EXECUTION_CONTEXT", context)
    observations = [
        {"name": "acceptance", "value": True, "source": "anonymous-adapter"},
        *[
            {"name": name, "value": True, "source": "anonymous-adapter"}
            for name in ("detect", "evidence", "plan", "apply", "verify", "rollback")
        ],
    ]
    receipt = _receipt(
        workspace,
        plan,
        stage=stage,
        context=context,
        check_id="repair_contract_complete",
        evidence_type="editor-audit",
        observations=observations,
        runtime_version=runtime,
        write_stage=True,
    )

    result = _record(workspace, plan, receipt, f"{route}-repair")

    assert result["status"] == "PASS"


@pytest.mark.parametrize(
    ("route", "stage", "context", "runtime"),
    [
        ("roadrunner-to-source-carla", "RR2SRC.OPTIMIZE", "source-unreal-python", "4.26.2-anonymous"),
        ("source-carla-to-package-carla", "SRC2PKG.OPTIMIZE", "source-unreal-python", "4.26.2-anonymous"),
        ("source-carla-to-ue427", "SRC2UE427.OPTIMIZE", "ue427-unreal-python", "4.27.2-anonymous"),
    ],
)
def test_all_three_routes_record_guarded_optimization_apply(
    workspace_factory, monkeypatch, route, stage, context, runtime
):
    workspace = workspace_factory(route)
    plan = _plan(workspace)
    _fake_unreal(monkeypatch, runtime)
    monkeypatch.setenv("CMTK_EXECUTION_CONTEXT", context)
    observations = [
        {"name": "acceptance", "value": True, "source": "anonymous-adapter"},
        {"name": "functional_baseline", "value": True, "source": "anonymous-adapter"},
        {"name": "protected_properties_unchanged", "value": True, "source": "anonymous-adapter"},
        {"name": "rollback", "value": True, "source": "anonymous-adapter"},
    ]
    receipt = _receipt(
        workspace,
        plan,
        stage=stage,
        context=context,
        check_id="optimization_apply_verified",
        evidence_type="editor-audit",
        observations=observations,
        runtime_version=runtime,
        write_stage=True,
    )

    result = _record(workspace, plan, receipt, f"{route}-optimization")

    assert result["status"] == "PASS"


def test_adapter_fails_closed_when_unreal_api_is_unavailable(workspace_factory, monkeypatch):
    workspace = workspace_factory("source-carla-to-ue427")
    plan = _plan(workspace)
    monkeypatch.setenv("CMTK_EXECUTION_CONTEXT", "source-unreal-python")
    monkeypatch.delitem(sys.modules, "unreal", raising=False)
    receipt = _receipt(
        workspace,
        plan,
        stage="SRC2UE427.BASELINE",
        context="source-unreal-python",
        check_id="source_asset_inventory_complete",
        evidence_type="deterministic-output",
        runtime_version="4.26.2-anonymous",
    )

    with pytest.raises(CmtkError, match="Unreal Python API") as captured:
        _record(workspace, plan, receipt, "missing-unreal")

    assert captured.value.reason_code == "ADAPTER-API-UNAVAILABLE"


def test_adapter_rejects_sensitive_artifact_content(workspace_factory, monkeypatch):
    workspace = workspace_factory("source-carla-to-ue427")
    plan = _plan(workspace)
    runtime = "4.26.2-anonymous"
    _fake_unreal(monkeypatch, runtime)
    monkeypatch.setenv("CMTK_EXECUTION_CONTEXT", "source-unreal-python")
    receipt = _receipt(
        workspace,
        plan,
        stage="SRC2UE427.BASELINE",
        context="source-unreal-python",
        check_id="source_asset_inventory_complete",
        evidence_type="deterministic-output",
        runtime_version=runtime,
    )
    artifact_path = Path(receipt["artifacts"][0]["local_path"])
    artifact_path.write_text('{"record":"private-anonymous-term"}\n', encoding="utf-8")
    receipt["artifacts"][0]["sha256"] = hashlib.sha256(artifact_path.read_bytes()).hexdigest()

    with pytest.raises(CmtkError, match="private or non-public-safe") as captured:
        _record(workspace, plan, receipt, "sensitive-artifact")

    assert captured.value.reason_code == "ADAPTER-SENSITIVE-DATA-DETECTED"


def test_repair_pass_requires_all_six_contract_observations(workspace_factory, monkeypatch):
    workspace = workspace_factory("roadrunner-to-source-carla")
    plan = _plan(workspace)
    runtime = "4.26.2-anonymous"
    _fake_unreal(monkeypatch, runtime)
    monkeypatch.setenv("CMTK_EXECUTION_CONTEXT", "source-unreal-python")
    receipt = _receipt(
        workspace,
        plan,
        stage="RR2SRC.REPAIR",
        context="source-unreal-python",
        check_id="repair_contract_complete",
        evidence_type="editor-audit",
        runtime_version=runtime,
        write_stage=True,
    )

    with pytest.raises(CmtkError, match="complete safety observations") as captured:
        _record(workspace, plan, receipt, "incomplete-repair")

    assert captured.value.reason_code == "ADAPTER-EVIDENCE-INVALID"


def test_adapter_rejects_malformed_receipt_before_context_use(workspace_factory):
    workspace = workspace_factory("source-carla-to-ue427")
    plan = _plan(workspace)
    receipt = _receipt(
        workspace,
        plan,
        stage="SRC2UE427.BASELINE",
        context="source-unreal-python",
        check_id="source_asset_inventory_complete",
        evidence_type="deterministic-output",
        runtime_version="4.26.2-anonymous",
    )
    receipt.pop("checks")

    with pytest.raises(CmtkError, match="does not satisfy its schema") as captured:
        _record(workspace, plan, receipt, "invalid-receipt")

    assert captured.value.reason_code == "ADAPTER-RECEIPT-INVALID"


def test_adapter_rejects_workspace_environment_mismatch(workspace_factory, monkeypatch):
    workspace = workspace_factory("source-carla-to-ue427")
    plan = _plan(workspace)
    runtime = "4.26.2-anonymous"
    _fake_unreal(monkeypatch, runtime)
    monkeypatch.setenv("CMTK_EXECUTION_CONTEXT", "source-unreal-python")
    receipt = _receipt(
        workspace,
        plan,
        stage="SRC2UE427.BASELINE",
        context="source-unreal-python",
        check_id="source_asset_inventory_complete",
        evidence_type="deterministic-output",
        runtime_version=runtime,
    )
    receipt["environment"]["source_carla_version"] = "0.0.0"

    with pytest.raises(CmtkError, match="fingerprinted workspace") as captured:
        _record(workspace, plan, receipt, "environment-mismatch")

    assert captured.value.reason_code == "ADAPTER-ENVIRONMENT-MISMATCH"


def test_write_stage_rejects_missing_rollback_contract(workspace_factory, monkeypatch):
    workspace = workspace_factory("source-carla-to-package-carla")
    plan = _plan(workspace)
    runtime = "4.26.2-anonymous"
    _fake_unreal(monkeypatch, runtime)
    monkeypatch.setenv("CMTK_EXECUTION_CONTEXT", "source-unreal-python")
    receipt = _receipt(
        workspace,
        plan,
        stage="SRC2PKG.REPAIR",
        context="source-unreal-python",
        check_id="repair_contract_complete",
        evidence_type="editor-audit",
        runtime_version=runtime,
        write_stage=False,
    )

    with pytest.raises(CmtkError, match="requires explicit apply mode") as captured:
        _record(workspace, plan, receipt, "missing-rollback")

    assert captured.value.reason_code == "ADAPTER-ROLLBACK-INCOMPLETE"


def test_adapter_requires_nonempty_sensitive_term_set(workspace_factory, monkeypatch):
    workspace = workspace_factory("source-carla-to-ue427")
    plan = _plan(workspace)
    runtime = "4.26.2-anonymous"
    _fake_unreal(monkeypatch, runtime)
    monkeypatch.setenv("CMTK_EXECUTION_CONTEXT", "source-unreal-python")
    receipt = _receipt(
        workspace,
        plan,
        stage="SRC2UE427.BASELINE",
        context="source-unreal-python",
        check_id="source_asset_inventory_complete",
        evidence_type="deterministic-output",
        runtime_version=runtime,
    )
    root = Path(workspace["execution"]["artifact_root"])
    terms = root / "empty-terms.txt"
    terms.write_text("# no approved terms\n", encoding="utf-8")

    with pytest.raises(CmtkError, match="at least one reviewed literal") as captured:
        record_stage_evidence(
            workspace,
            plan,
            receipt,
            output_dir=str(root / "empty-terms-evidence"),
            evidence_prefix="evidence/anonymous/stages/empty-terms",
            sensitive_terms_path=str(terms),
        )

    assert captured.value.reason_code == "ADAPTER-SENSITIVE-TERMS-REQUIRED"


def test_adapter_rejects_non_repository_public_path(workspace_factory, monkeypatch):
    workspace = workspace_factory("source-carla-to-ue427")
    plan = _plan(workspace)
    runtime = "4.26.2-anonymous"
    _fake_unreal(monkeypatch, runtime)
    monkeypatch.setenv("CMTK_EXECUTION_CONTEXT", "source-unreal-python")
    receipt = _receipt(
        workspace,
        plan,
        stage="SRC2UE427.BASELINE",
        context="source-unreal-python",
        check_id="source_asset_inventory_complete",
        evidence_type="deterministic-output",
        runtime_version=runtime,
    )
    receipt["artifacts"][0]["public_path"] = "../private/artifact.json"

    with pytest.raises(CmtkError, match="public evidence directory") as captured:
        _record(workspace, plan, receipt, "invalid-public-path")

    assert captured.value.reason_code == "ADAPTER-PUBLIC-PATH-INVALID"


def test_adapter_rejects_empty_repository_public_path_without_crashing(workspace_factory, monkeypatch):
    workspace = workspace_factory("source-carla-to-ue427")
    plan = _plan(workspace)
    runtime = "4.26.2-anonymous"
    _fake_unreal(monkeypatch, runtime)
    monkeypatch.setenv("CMTK_EXECUTION_CONTEXT", "source-unreal-python")
    receipt = _receipt(
        workspace,
        plan,
        stage="SRC2UE427.BASELINE",
        context="source-unreal-python",
        check_id="source_asset_inventory_complete",
        evidence_type="deterministic-output",
        runtime_version=runtime,
    )
    receipt["artifacts"][0]["public_path"] = "."

    with pytest.raises(CmtkError, match="public evidence directory") as captured:
        _record(workspace, plan, receipt, "empty-public-path")

    assert captured.value.reason_code == "ADAPTER-PUBLIC-PATH-INVALID"


def test_adapter_rejects_incomplete_required_stage_receipt(workspace_factory, monkeypatch):
    workspace = workspace_factory("source-carla-to-ue427")
    plan = _plan(workspace)
    runtime = "4.27.2-anonymous"
    _fake_unreal(monkeypatch, runtime)
    monkeypatch.setenv("CMTK_EXECUTION_CONTEXT", "ue427-unreal-python")
    receipt = _receipt(
        workspace,
        plan,
        stage="SRC2UE427.TARGET_VALIDATE",
        context="ue427-unreal-python",
        check_id="target_reopen",
        evidence_type="editor-audit",
        runtime_version=runtime,
        complete_stage=False,
    )

    with pytest.raises(CmtkError, match="missing required checks") as captured:
        _record(workspace, plan, receipt, "incomplete-target-stage")

    assert captured.value.reason_code == "ADAPTER-EVIDENCE-INVALID"
    assert "missing_check_ids" in captured.value.details


@pytest.mark.parametrize(
    ("status", "acceptance"),
    [("PASS", False), ("FAIL", True), ("PASS", 1)],
)
def test_adapter_rejects_check_status_that_conflicts_with_acceptance(
    workspace_factory, monkeypatch, status, acceptance
):
    workspace = workspace_factory("source-carla-to-ue427")
    plan = _plan(workspace)
    runtime = "4.26.2-anonymous"
    _fake_unreal(monkeypatch, runtime)
    monkeypatch.setenv("CMTK_EXECUTION_CONTEXT", "source-unreal-python")
    receipt = _receipt(
        workspace,
        plan,
        stage="SRC2UE427.BASELINE",
        context="source-unreal-python",
        check_id="source_asset_inventory_complete",
        evidence_type="deterministic-output",
        runtime_version=runtime,
    )
    receipt["checks"][0]["status"] = status
    receipt["checks"][0]["observations"] = [
        {"name": "acceptance", "value": acceptance, "source": "anonymous-conflict"}
    ]

    with pytest.raises(CmtkError, match="explicit boolean acceptance") as captured:
        _record(workspace, plan, receipt, f"conflicting-acceptance-{status.lower()}")

    assert captured.value.reason_code == "ADAPTER-EVIDENCE-INVALID"


def test_failed_stage_has_no_next_allowed_stage(workspace_factory, monkeypatch):
    workspace = workspace_factory("source-carla-to-ue427")
    plan = _plan(workspace)
    runtime = "4.26.2-anonymous"
    _fake_unreal(monkeypatch, runtime)
    monkeypatch.setenv("CMTK_EXECUTION_CONTEXT", "source-unreal-python")
    receipt = _receipt(
        workspace,
        plan,
        stage="SRC2UE427.BASELINE",
        context="source-unreal-python",
        check_id="source_asset_inventory_complete",
        evidence_type="deterministic-output",
        runtime_version=runtime,
    )
    receipt["checks"][0]["status"] = "FAIL"
    receipt["checks"][0]["summary"] = "The anonymous baseline did not pass."
    receipt["checks"][0]["observations"] = [
        {"name": "acceptance", "value": False, "source": "anonymous-adapter"}
    ]

    result = _record(workspace, plan, receipt, "failed-stage")

    assert result["status"] == "FAIL"
    assert result["next_allowed_stages"] == []


def test_context_receipt_script_uses_python37_compatible_syntax():
    ast.parse(
        CONTEXT_RECEIPT.read_text(encoding="utf-8"),
        filename=str(CONTEXT_RECEIPT),
        feature_version=(3, 7),
    )


def test_unreal_context_can_finalize_then_host_can_record_receipt(
    workspace_factory, monkeypatch, tmp_path
):
    workspace = workspace_factory("source-carla-to-ue427")
    plan = _plan(workspace)
    runtime = "4.26.2-anonymous"
    receipt = _receipt(
        workspace,
        plan,
        stage="SRC2UE427.BASELINE",
        context="source-unreal-python",
        check_id="source_asset_inventory_complete",
        evidence_type="deterministic-output",
        runtime_version=runtime,
    )
    root = Path(workspace["execution"]["artifact_root"])
    config_path = tmp_path / "workspace.json"
    plan_path = root / "route-plan.json"
    draft_path = root / "receipt-draft.json"
    finalized_path = root / "receipt-finalized.json"
    config_path.write_text(json.dumps(workspace), encoding="utf-8")
    plan_path.write_text(json.dumps(plan), encoding="utf-8")
    draft_path.write_text(json.dumps(receipt), encoding="utf-8")
    fake_root = tmp_path / "fake-unreal"
    fake_root.mkdir()
    (fake_root / "unreal.py").write_text(
        "class SystemLibrary:\n"
        "    @staticmethod\n"
        "    def get_engine_version():\n"
        f"        return {runtime!r}\n",
        encoding="utf-8",
    )

    finalized = subprocess.run(
        [
            sys.executable,
            str(CONTEXT_RECEIPT),
            "--config",
            str(config_path),
            "--plan",
            str(plan_path),
            "--receipt-draft",
            str(draft_path),
            "--output",
            str(finalized_path),
        ],
        check=False,
        capture_output=True,
        text=True,
        env={
            **os.environ,
            "CMTK_EXECUTION_CONTEXT": "source-unreal-python",
            "PYTHONPATH": os.pathsep.join([str(fake_root), os.environ.get("PYTHONPATH", "")]),
            "PYTHONDONTWRITEBYTECODE": "1",
        },
    )
    assert finalized.returncode == 0, finalized.stdout
    finalized_receipt = json.loads(finalized_path.read_text(encoding="utf-8"))
    assert finalized_receipt["boundary"]["observed_context"] == "source-unreal-python"

    monkeypatch.setenv("CMTK_EXECUTION_CONTEXT", "host-cpython")
    result = _record(workspace, plan, finalized_receipt, "host-recorded-finalized")

    assert result["status"] == "PASS"


@pytest.mark.parametrize(
    ("route", "stage", "context", "check_id", "evidence_type", "runtime", "write_stage"),
    [
        (
            "source-carla-to-ue427",
            "SRC2UE427.TARGET_VALIDATE",
            "ue427-unreal-python",
            "target_reopen",
            "editor-audit",
            "4.27.2-anonymous",
            False,
        ),
        (
            "source-carla-to-package-carla",
            "SRC2PKG.RUNTIME_VALIDATE",
            "carla-client-python",
            "dynamic_smoke",
            "runtime-measurement",
            "",
            False,
        ),
        (
            "source-carla-to-package-carla",
            "SRC2PKG.BUILD",
            "shell-build",
            "package_artifact_hashed",
            "deterministic-output",
            "",
            True,
        ),
    ],
)
def test_remaining_contexts_finalize_portable_boundary_receipts(
    workspace_factory,
    tmp_path,
    route,
    stage,
    context,
    check_id,
    evidence_type,
    runtime,
    write_stage,
):
    workspace = workspace_factory(route)
    plan = _plan(workspace)
    receipt = _receipt(
        workspace,
        plan,
        stage=stage,
        context=context,
        check_id=check_id,
        evidence_type=evidence_type,
        runtime_version=runtime,
        write_stage=write_stage,
    )
    root = Path(workspace["execution"]["artifact_root"])
    config_path = tmp_path / f"{context}-workspace.json"
    plan_path = root / f"{context}-route-plan.json"
    draft_path = root / f"{context}-draft.json"
    finalized_path = root / f"{context}-finalized.json"
    config_path.write_text(json.dumps(workspace), encoding="utf-8")
    plan_path.write_text(json.dumps(plan), encoding="utf-8")
    draft_path.write_text(json.dumps(receipt), encoding="utf-8")
    fake_root = tmp_path / f"fake-{context}"
    fake_root.mkdir()
    if "unreal" in context:
        (fake_root / "unreal.py").write_text(
            "class SystemLibrary:\n"
            "    @staticmethod\n"
            "    def get_engine_version():\n"
            f"        return {runtime!r}\n",
            encoding="utf-8",
        )
    if context == "carla-client-python":
        (fake_root / "carla.py").write_text("class Client:\n    pass\n", encoding="utf-8")

    finalized = subprocess.run(
        [
            sys.executable,
            str(CONTEXT_RECEIPT),
            "--config",
            str(config_path),
            "--plan",
            str(plan_path),
            "--receipt-draft",
            str(draft_path),
            "--output",
            str(finalized_path),
        ],
        check=False,
        capture_output=True,
        text=True,
        env={
            **os.environ,
            "CMTK_EXECUTION_CONTEXT": context,
            "PYTHONPATH": os.pathsep.join([str(fake_root), os.environ.get("PYTHONPATH", "")]),
            "PYTHONDONTWRITEBYTECODE": "1",
        },
    )

    assert finalized.returncode == 0, finalized.stdout
    payload = json.loads(finalized_path.read_text(encoding="utf-8"))
    assert payload["boundary"]["observed_context"] == context


def test_host_rejects_tampered_finalized_boundary(workspace_factory, monkeypatch):
    workspace = workspace_factory("source-carla-to-ue427")
    plan = _plan(workspace)
    runtime = "4.26.2-anonymous"
    receipt = _receipt(
        workspace,
        plan,
        stage="SRC2UE427.BASELINE",
        context="source-unreal-python",
        check_id="source_asset_inventory_complete",
        evidence_type="deterministic-output",
        runtime_version=runtime,
    )
    receipt["boundary"] = {
        "schema_version": "1.0.0",
        "adapter": "cmtk-context-receipt",
        "adapter_sha256": "a" * 64,
        "draft_sha256": "b" * 64,
        "observed_context": "source-unreal-python",
        "observed_api_version": runtime,
        "finalized_at": "2026-08-28T00:00:00Z",
    }
    monkeypatch.setenv("CMTK_EXECUTION_CONTEXT", "host-cpython")

    with pytest.raises(CmtkError, match="boundary proof") as captured:
        _record(workspace, plan, receipt, "tampered-boundary")

    assert captured.value.reason_code == "ADAPTER-RECEIPT-INVALID"


def test_host_rejects_non_utc_boundary_timestamp(workspace_factory, monkeypatch):
    workspace = workspace_factory("source-carla-to-ue427")
    plan = _plan(workspace)
    runtime = "4.26.2-anonymous"
    receipt = _receipt(
        workspace,
        plan,
        stage="SRC2UE427.BASELINE",
        context="source-unreal-python",
        check_id="source_asset_inventory_complete",
        evidence_type="deterministic-output",
        runtime_version=runtime,
    )
    receipt["boundary"] = {
        "schema_version": "1.0.0",
        "adapter": "cmtk-context-receipt",
        "adapter_sha256": evidence_adapter.sha256_file(CONTEXT_RECEIPT),
        "draft_sha256": evidence_adapter.sha256_json(receipt),
        "observed_context": "source-unreal-python",
        "observed_api_version": runtime,
        "finalized_at": "not-a-timestamp",
    }
    monkeypatch.setenv("CMTK_EXECUTION_CONTEXT", "host-cpython")

    with pytest.raises(CmtkError, match="Boundary finalized_at") as captured:
        _record(workspace, plan, receipt, "invalid-boundary-timestamp")

    assert captured.value.reason_code == "ADAPTER-RECEIPT-INVALID"


def test_adapter_rejects_duplicate_public_file_paths(workspace_factory, monkeypatch):
    workspace = workspace_factory("source-carla-to-ue427")
    plan = _plan(workspace)
    runtime = "4.26.2-anonymous"
    _fake_unreal(monkeypatch, runtime)
    monkeypatch.setenv("CMTK_EXECUTION_CONTEXT", "source-unreal-python")
    receipt = _receipt(
        workspace,
        plan,
        stage="SRC2UE427.BASELINE",
        context="source-unreal-python",
        check_id="source_asset_inventory_complete",
        evidence_type="deterministic-output",
        runtime_version=runtime,
    )
    receipt["inputs"] = [dict(receipt["artifacts"][0])]

    with pytest.raises(CmtkError, match="public paths must be unique") as captured:
        _record(workspace, plan, receipt, "duplicate-public-path")

    assert captured.value.reason_code == "ADAPTER-EVIDENCE-INVALID"


def test_adapter_rejects_artifact_path_that_collides_with_stage_result(
    workspace_factory, monkeypatch
):
    workspace = workspace_factory("source-carla-to-ue427")
    plan = _plan(workspace)
    runtime = "4.26.2-anonymous"
    _fake_unreal(monkeypatch, runtime)
    monkeypatch.setenv("CMTK_EXECUTION_CONTEXT", "source-unreal-python")
    receipt = _receipt(
        workspace,
        plan,
        stage="SRC2UE427.BASELINE",
        context="source-unreal-python",
        check_id="source_asset_inventory_complete",
        evidence_type="deterministic-output",
        runtime_version=runtime,
    )
    receipt["artifacts"][0]["public_path"] = (
        "evidence/anonymous/stages/stage-result-collision/stage-result.json"
    )

    with pytest.raises(CmtkError, match="public paths must be unique") as captured:
        _record(workspace, plan, receipt, "stage-result-collision")

    assert captured.value.reason_code == "ADAPTER-EVIDENCE-INVALID"


def test_repair_pass_rejects_conflicting_duplicate_phase_observation(workspace_factory, monkeypatch):
    workspace = workspace_factory("roadrunner-to-source-carla")
    plan = _plan(workspace)
    runtime = "4.26.2-anonymous"
    _fake_unreal(monkeypatch, runtime)
    monkeypatch.setenv("CMTK_EXECUTION_CONTEXT", "source-unreal-python")
    observations = [
        {"name": "acceptance", "value": True, "source": "anonymous-adapter"},
        {"name": "detect", "value": False, "source": "anonymous-conflict"},
        *[
            {"name": name, "value": True, "source": "anonymous-adapter"}
            for name in ("detect", "evidence", "plan", "apply", "verify", "rollback")
        ],
    ]
    receipt = _receipt(
        workspace,
        plan,
        stage="RR2SRC.REPAIR",
        context="source-unreal-python",
        check_id="repair_contract_complete",
        evidence_type="editor-audit",
        observations=observations,
        runtime_version=runtime,
        write_stage=True,
    )

    with pytest.raises(CmtkError, match="complete safety observations") as captured:
        _record(workspace, plan, receipt, "conflicting-repair")

    assert captured.value.reason_code == "ADAPTER-EVIDENCE-INVALID"


def test_adapter_bounds_public_supporting_artifact_size(workspace_factory, monkeypatch):
    workspace = workspace_factory("source-carla-to-ue427")
    plan = _plan(workspace)
    runtime = "4.26.2-anonymous"
    _fake_unreal(monkeypatch, runtime)
    monkeypatch.setenv("CMTK_EXECUTION_CONTEXT", "source-unreal-python")
    monkeypatch.setattr(evidence_adapter, "MAX_PUBLIC_EVIDENCE_BYTES", 8)
    receipt = _receipt(
        workspace,
        plan,
        stage="SRC2UE427.BASELINE",
        context="source-unreal-python",
        check_id="source_asset_inventory_complete",
        evidence_type="deterministic-output",
        runtime_version=runtime,
    )

    with pytest.raises(CmtkError, match="size limit") as captured:
        _record(workspace, plan, receipt, "oversized-artifact")

    assert captured.value.reason_code == "ADAPTER-EVIDENCE-INVALID"


@pytest.mark.parametrize("recorded_at", ["not-a-timestamp", "2026-08-28Z"])
def test_adapter_rejects_non_utc_receipt_timestamp(workspace_factory, monkeypatch, recorded_at):
    workspace = workspace_factory("source-carla-to-ue427")
    plan = _plan(workspace)
    runtime = "4.26.2-anonymous"
    _fake_unreal(monkeypatch, runtime)
    monkeypatch.setenv("CMTK_EXECUTION_CONTEXT", "source-unreal-python")
    receipt = _receipt(
        workspace,
        plan,
        stage="SRC2UE427.BASELINE",
        context="source-unreal-python",
        check_id="source_asset_inventory_complete",
        evidence_type="deterministic-output",
        runtime_version=runtime,
    )
    receipt["recorded_at"] = recorded_at

    with pytest.raises(CmtkError, match="UTC timestamp") as captured:
        _record(workspace, plan, receipt, "invalid-timestamp")

    assert captured.value.reason_code == "ADAPTER-RECEIPT-INVALID"
