from copy import deepcopy
from pathlib import Path

import pytest
from cmtk.core.errors import CmtkError
from cmtk.core.hashing import sha256_json
from cmtk.core.plans import (
    seal_plan,
    verify_input_fingerprints,
    verify_plan,
    verify_workspace_fingerprint,
)
from cmtk.routes import source_to_ue427
from cmtk.routes.inspection import inspect_workspace
from cmtk.routes.planning import build_plan


def _built_plan(workspace_factory, route: str) -> tuple[dict, dict]:
    workspace = workspace_factory(route)
    return workspace, build_plan(workspace, route, inspect_workspace(workspace, route))


def test_plan_hash_is_canonical_and_verifiable(workspace_factory):
    _, plan = _built_plan(workspace_factory, "source-carla-to-package-carla")
    assert plan["plan_sha256"] == sha256_json({k: v for k, v in plan.items() if k != "plan_sha256"})
    verify_plan(plan, expected_sha256=plan["plan_sha256"])


def test_plan_verification_detects_tampering(workspace_factory):
    _, plan = _built_plan(workspace_factory, "source-carla-to-package-carla")
    changed = deepcopy(plan)
    changed["route"] = "source-carla-to-ue427"
    with pytest.raises(CmtkError) as error:
        verify_plan(changed, expected_sha256=plan["plan_sha256"])
    assert error.value.reason_code == "PLAN-HASH-MISMATCH"


def test_plan_verification_rejects_pre_migration_schema_version():
    plan = seal_plan(
        {
            "schema_version": "1.1.0",
            "plan_id": "stale-plan",
            "route": "source-carla-to-ue427",
            "created_at": "2026-08-26T00:00:00Z",
            "workspace_sha256": "a" * 64,
            "input_fingerprints": [],
            "environment_fingerprints": [],
            "steps": [],
            "blocked_reasons": [],
        }
    )
    with pytest.raises(CmtkError) as error:
        verify_plan(plan)
    assert error.value.reason_code == "SCHEMA-VERSION-UNSUPPORTED"


def test_plan_verification_rejects_malformed_dependency_action(workspace_factory):
    _, plan = _built_plan(workspace_factory, "source-carla-to-ue427")
    next(step for step in plan["steps"] if step["step_id"] == "SRC2UE427.CLASSIFY_DEPS")["assets"] = [{}]
    plan = seal_plan(plan)
    with pytest.raises(CmtkError) as error:
        verify_plan(plan)
    assert error.value.reason_code == "PLAN-INVALID"


def test_plan_verification_rejects_semantically_empty_dependency_action(workspace_factory):
    _, plan = _built_plan(workspace_factory, "source-carla-to-ue427")
    next(step for step in plan["steps"] if step["step_id"] == "SRC2UE427.CLASSIFY_DEPS")["assets"] = [
        {
            "source_object": None,
            "classification": "portable",
            "target_strategy": None,
            "referencers": [],
            "migration_action": None,
            "verification": [],
            "rollback": [],
            "residual_risk": None,
        }
    ]
    plan = seal_plan(plan)
    with pytest.raises(CmtkError) as error:
        verify_plan(plan)
    assert error.value.reason_code == "PLAN-INVALID"


def test_plan_verification_rejects_missing_route_steps(workspace_factory):
    workspace, plan = _built_plan(workspace_factory, "source-carla-to-ue427")
    plan["steps"] = []
    plan = seal_plan(plan)

    with pytest.raises(CmtkError) as workspace_error:
        verify_workspace_fingerprint(plan, workspace)
    assert workspace_error.value.reason_code == "PLAN-INVALID"
    verify_input_fingerprints(plan, workspace["execution"]["allowed_roots"])
    with pytest.raises(CmtkError) as error:
        verify_plan(plan)
    assert error.value.reason_code == "PLAN-INVALID"


def test_plan_verification_rejects_tampered_stage_safety_metadata(workspace_factory):
    workspace, plan = _built_plan(workspace_factory, "source-carla-to-ue427")
    migrate = next(step for step in plan["steps"] if step["step_id"] == "SRC2UE427.MIGRATE_ASSETS")
    migrate.update({"type": "AUTO", "execution_context": "host-cpython", "risk": "low"})
    plan = seal_plan(plan)

    verify_workspace_fingerprint(plan, workspace)
    verify_input_fingerprints(plan, workspace["execution"]["allowed_roots"])
    with pytest.raises(CmtkError) as error:
        verify_plan(plan)
    assert error.value.reason_code == "PLAN-INVALID"


def test_plan_verification_rejects_filesystem_root_stage_path(workspace_factory):
    _, plan = _built_plan(workspace_factory, "source-carla-to-ue427")
    migrate = next(step for step in plan["steps"] if step["step_id"] == "SRC2UE427.MIGRATE_ASSETS")
    migrate["write_paths"] = ["/"]
    plan = seal_plan(plan)

    with pytest.raises(CmtkError) as error:
        verify_plan(plan)
    assert error.value.reason_code == "PATH-TARGET-AMBIGUOUS"


def test_workspace_verification_rejects_resealed_stage_path_drift(workspace_factory):
    workspace, plan = _built_plan(workspace_factory, "source-carla-to-ue427")
    migrate = next(step for step in plan["steps"] if step["step_id"] == "SRC2UE427.MIGRATE_ASSETS")
    migrate["write_paths"] = [workspace["execution"]["artifact_root"]]
    plan = seal_plan(plan)

    verify_plan(plan)
    with pytest.raises(CmtkError) as error:
        verify_workspace_fingerprint(plan, workspace)
    assert error.value.reason_code == "PLAN-INVALID"


def test_route_plan_fingerprints_explicit_roadrunner_inputs(workspace_factory):
    workspace = workspace_factory("roadrunner-to-source-carla")
    inspection = inspect_workspace(workspace, "roadrunner-to-source-carla")
    plan = build_plan(workspace, "roadrunner-to-source-carla", inspection)
    fingerprints = plan["input_fingerprints"]
    assert {item["name"] for item in fingerprints} == {"ExampleMap.udatasmith", "ExampleMap.xodr"}
    assert all(len(item["sha256"]) == 64 for item in fingerprints)
    assert all(item["size_bytes"] > 0 for item in fingerprints)


def test_input_fingerprint_change_makes_plan_stale(workspace_factory):
    workspace = workspace_factory("roadrunner-to-source-carla")
    inspection = inspect_workspace(workspace, "roadrunner-to-source-carla")
    plan = build_plan(workspace, "roadrunner-to-source-carla", inspection)
    changed = Path(workspace["input"]["root"]) / "ExampleMap.xodr"
    changed.write_text("<OpenDRIVE><changed/></OpenDRIVE>\n", encoding="utf-8")
    with pytest.raises(CmtkError) as error:
        verify_input_fingerprints(plan, workspace["execution"]["allowed_roots"])
    assert error.value.reason_code == "PLAN-STALE"


@pytest.mark.parametrize("route", ["source-carla-to-package-carla", "source-carla-to-ue427"])
def test_downstream_plans_fingerprint_handoff_and_source_manifests(route, workspace_factory):
    workspace = workspace_factory(route)
    inspection = inspect_workspace(workspace, route)
    plan = build_plan(workspace, route, inspection)
    assert {item["kind"] for item in plan["input_fingerprints"]} == {
        "map-handoff",
        "source-asset-inventory",
        "source-dependency-manifest",
        "route-input-manifest",
        "opendrive",
    }

    changed = Path(workspace["input"]["asset_inventory_path"])
    changed.write_text('{"assets":["changed"]}\n', encoding="utf-8")
    with pytest.raises(CmtkError) as error:
        verify_input_fingerprints(plan, workspace["execution"]["allowed_roots"])
    assert error.value.reason_code == "PLAN-STALE"


def test_ue427_plan_actions_and_dependency_fingerprint_use_one_snapshot(workspace_factory, monkeypatch):
    route = "source-carla-to-ue427"
    workspace = workspace_factory(route)
    manifest = Path(workspace["input"]["dependency_manifest_path"])
    original_hash = next(
        item["sha256"]
        for item in build_plan(workspace, route, inspect_workspace(workspace, route))["input_fingerprints"]
        if item["kind"] == "source-dependency-manifest"
    )
    original_load_json = source_to_ue427.load_json
    inspection = inspect_workspace(workspace, route)

    def load_then_replace(path):
        value = original_load_json(path)
        manifest.write_text('{"dependencies":[]}\n', encoding="utf-8")
        return value

    monkeypatch.setattr(source_to_ue427, "load_json", load_then_replace)
    plan = build_plan(workspace, route, inspection)
    dependency_fingerprint = next(
        item for item in plan["input_fingerprints"] if item["kind"] == "source-dependency-manifest"
    )
    classify_step = next(step for step in plan["steps"] if step["step_id"] == "SRC2UE427.CLASSIFY_DEPS")

    assert dependency_fingerprint["sha256"] == original_hash
    assert classify_step["assets"][0]["source_object"] == "/Game/Maps/Example/Road"


def test_missing_required_input_fingerprint_is_rejected(workspace_factory):
    route = "source-carla-to-package-carla"
    workspace = workspace_factory(route)
    inspection = inspect_workspace(workspace, route)
    plan = build_plan(workspace, route, inspection)
    plan["input_fingerprints"] = [
        item for item in plan["input_fingerprints"] if item["kind"] != "source-asset-inventory"
    ]

    with pytest.raises(CmtkError) as error:
        verify_input_fingerprints(plan, workspace["execution"]["allowed_roots"])
    assert error.value.reason_code == "PLAN-INPUT-FINGERPRINTS-INCOMPLETE"


def test_workspace_and_plan_route_must_match(workspace_factory):
    workspace = workspace_factory("source-carla-to-package-carla")
    plan = {"route": "source-carla-to-ue427", "workspace_sha256": sha256_json(workspace)}

    with pytest.raises(CmtkError) as error:
        verify_workspace_fingerprint(plan, workspace)
    assert error.value.reason_code == "ROUTE-CONFLICT"


def test_package_plan_scopes_source_build_and_target_import_separately(workspace_factory):
    workspace = workspace_factory("source-carla-to-package-carla")
    inspection = inspect_workspace(workspace, "source-carla-to-package-carla")
    plan = build_plan(workspace, "source-carla-to-package-carla", inspection)
    steps = {item["step_id"]: item for item in plan["steps"]}
    assert workspace["source_carla"]["root"] in steps["SRC2PKG.BUILD"]["write_paths"]
    assert workspace["package_carla"]["root"] not in steps["SRC2PKG.BUILD"]["write_paths"]
    assert steps["SRC2PKG.IMPORT"]["write_paths"] == [workspace["package_carla"]["root"]]


def test_ue427_cold_copy_step_targets_cold_project_not_uproject_file(workspace_factory):
    workspace = workspace_factory("source-carla-to-ue427")
    inspection = inspect_workspace(workspace, "source-carla-to-ue427")
    plan = build_plan(workspace, "source-carla-to-ue427", inspection)
    steps = {item["step_id"]: item for item in plan["steps"]}
    cold_project_root = str(Path(workspace["ue427"]["cold_copy_uproject"]).parent)
    target_project_root = str(Path(workspace["ue427"]["uproject"]).parent)
    assert steps["SRC2UE427.COLD_COPY"]["write_paths"] == [cold_project_root]
    assert steps["SRC2UE427.MIGRATE_ASSETS"]["write_paths"] == [
        workspace["source_carla"]["root"],
        target_project_root,
    ]
