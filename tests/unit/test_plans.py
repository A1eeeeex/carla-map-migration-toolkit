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
from cmtk.routes.inspection import inspect_workspace
from cmtk.routes.planning import build_plan


def test_plan_hash_is_canonical_and_verifiable():
    plan = {
        "schema_version": "1.0.0",
        "plan_id": "plan-example",
        "route": "source-carla-to-ue427",
        "created_at": "2026-08-26T00:00:00Z",
        "workspace_sha256": "a" * 64,
        "input_fingerprints": [],
        "environment_fingerprints": [],
        "steps": [],
        "blocked_reasons": [],
    }
    sealed = seal_plan(plan)
    assert sealed["plan_sha256"] == sha256_json({k: v for k, v in sealed.items() if k != "plan_sha256"})
    verify_plan(sealed, expected_sha256=sealed["plan_sha256"])


def test_plan_verification_detects_tampering():
    plan = seal_plan(
        {
            "schema_version": "1.0.0",
            "plan_id": "plan-example",
            "route": "source-carla-to-package-carla",
            "created_at": "2026-08-26T00:00:00Z",
            "workspace_sha256": "b" * 64,
            "input_fingerprints": [],
            "environment_fingerprints": [],
            "steps": [],
            "blocked_reasons": [],
        }
    )
    changed = deepcopy(plan)
    changed["route"] = "source-carla-to-ue427"
    with pytest.raises(CmtkError) as error:
        verify_plan(changed, expected_sha256=plan["plan_sha256"])
    assert error.value.reason_code == "PLAN-HASH-MISMATCH"


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
    assert steps["SRC2UE427.MIGRATE_ASSETS"]["write_paths"] == [target_project_root]
