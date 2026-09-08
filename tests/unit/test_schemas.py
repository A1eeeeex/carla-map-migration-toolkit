from __future__ import annotations

import json

import jsonschema
import pytest
from cmtk.routes.catalog import REQUIRED_CHECK_EVIDENCE_TYPES, REQUIRED_CHECK_STAGES
from cmtk.routes.inspection import inspect_workspace
from cmtk.routes.planning import build_plan
from cmtk.validation.reporting import pending_validation_report
from conftest import PLUGIN_ROOT

SCHEMA_NAMES = {
    "adapter-receipt",
    "check-evidence",
    "claims-registry",
    "map-workspace",
    "redaction-report",
    "route-plan",
    "stage-result",
    "map-handoff",
    "validation-report",
    "verified-run",
    "compatibility-matrix",
}


@pytest.mark.parametrize("name", sorted(SCHEMA_NAMES))
def test_public_example_conforms_to_versioned_schema(name: str):
    schema = json.loads((PLUGIN_ROOT / "schemas" / f"{name}.schema.json").read_text(encoding="utf-8"))
    example = json.loads((PLUGIN_ROOT / "examples" / f"{name}.example.json").read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(example, schema)


def test_stage_result_schema_rejects_success_alias():
    schema = json.loads((PLUGIN_ROOT / "schemas" / "stage-result.schema.json").read_text(encoding="utf-8"))
    example = json.loads((PLUGIN_ROOT / "examples" / "stage-result.example.json").read_text(encoding="utf-8"))
    example["status"] = "SUCCESS"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(example, schema)


def test_verified_run_pass_rejects_required_not_run():
    schema = json.loads((PLUGIN_ROOT / "schemas" / "verified-run.schema.json").read_text(encoding="utf-8"))
    example = json.loads((PLUGIN_ROOT / "examples" / "verified-run.example.json").read_text(encoding="utf-8"))
    example["status"] = "PASS"
    example["evidence_level"] = "L5"
    example["required_checks"][-1]["status"] = "PASS"
    example["redaction"] = {"status": "PASS", "report": "redaction-report.json"}
    example["signoff"].update(
        {
            "runner": "maintainer",
            "reviewer": "reviewer",
            "date": "2026-08-26",
            "evidence_sha256": "a" * 64,
        }
    )
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(example, schema)


def test_verified_run_rejects_sparse_source_to_ue427_pass():
    schema = json.loads((PLUGIN_ROOT / "schemas" / "verified-run.schema.json").read_text(encoding="utf-8"))
    example = json.loads((PLUGIN_ROOT / "examples" / "verified-run.example.json").read_text(encoding="utf-8"))
    example.update(
        {
            "status": "PASS",
            "evidence_level": "L5",
            "environment": {},
            "input_hashes": [],
            "target_identity": {},
            "stage_results": [],
            "artifacts": [],
            "required_checks": [
                {
                    "id": "second_clean_project_cold_copy",
                    "required": True,
                    "status": "PASS",
                    "evidence": [],
                }
            ],
            "redaction": {"status": "PASS", "report": "redaction-report.json"},
        }
    )
    example["signoff"].update(
        {
            "runner": "maintainer",
            "reviewer": "reviewer",
            "date": "2026-08-26",
            "evidence_sha256": "a" * 64,
        }
    )
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(example, schema)


@pytest.mark.parametrize(
    "route",
    ["roadrunner-to-source-carla", "source-carla-to-package-carla"],
)
def test_verified_run_rejects_sparse_pass_for_other_routes(route: str):
    schema = json.loads((PLUGIN_ROOT / "schemas" / "verified-run.schema.json").read_text(encoding="utf-8"))
    example = json.loads((PLUGIN_ROOT / "examples" / "verified-run.example.json").read_text(encoding="utf-8"))
    example.update(
        {
            "route": route,
            "status": "PASS",
            "evidence_level": "L0",
            "environment": {"host_os": "anonymous-linux"},
            "input_hashes": [{"path": "input.json", "sha256": "a" * 64}],
            "target_identity": {"project_fingerprint": "anonymous"},
            "claims_evaluated": ["C-RR-SRC-001"],
            "required_checks": [
                {"id": "arbitrary", "required": True, "status": "PASS", "evidence": ["evidence.json"]}
            ],
            "stage_results": ["stage.json"],
            "protected_property_diff": {"status": "PASS"},
            "artifacts": [{"path": "evidence.json", "sha256": "b" * 64}],
            "redaction": {"status": "PASS", "report": "redaction.json"},
        }
    )
    example["signoff"].update(
        {
            "runner": "maintainer",
            "reviewer": "reviewer",
            "date": "2026-08-26",
            "evidence_sha256": "b" * 64,
        }
    )
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(example, schema)


def test_breaking_phase_a_contracts_use_new_schema_version():
    versions = {
        "claims-registry": "1.2.0",
        "check-evidence": "1.1.0",
        "compatibility-matrix": "1.1.0",
        "route-plan": "1.5.0",
        "verified-run": "1.4.0",
    }
    for name, expected in versions.items():
        schema = json.loads((PLUGIN_ROOT / "schemas" / f"{name}.schema.json").read_text(encoding="utf-8"))
        example = json.loads((PLUGIN_ROOT / "examples" / f"{name}.example.json").read_text(encoding="utf-8"))
        assert schema["properties"]["schema_version"]["const"] == expected
        assert example["schema_version"] == expected


@pytest.mark.parametrize(
    ("check_id", "valid_type", "invalid_type"),
    [
        ("dependency_classification_complete", "deterministic-output", "manual-review"),
        ("target_reopen", "editor-audit", "manual-review"),
        ("pie_smoke", "runtime-measurement", "manual-review"),
        ("second_clean_project_cold_copy", "portability-replay", "manual-review"),
    ],
)
def test_required_check_evidence_type_is_bound(check_id, valid_type, invalid_type):
    schema = json.loads((PLUGIN_ROOT / "schemas" / "check-evidence.schema.json").read_text(encoding="utf-8"))
    example = json.loads((PLUGIN_ROOT / "examples" / "check-evidence.example.json").read_text(encoding="utf-8"))
    example.update({"check_id": check_id, "evidence_type": valid_type})
    jsonschema.validate(example, schema)
    example["evidence_type"] = invalid_type
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(example, schema)


def test_pass_check_evidence_requires_positive_acceptance_observation():
    schema = json.loads((PLUGIN_ROOT / "schemas" / "check-evidence.schema.json").read_text(encoding="utf-8"))
    example = json.loads((PLUGIN_ROOT / "examples" / "check-evidence.example.json").read_text(encoding="utf-8"))
    example["observations"][0]["value"] = False
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(example, schema)


def test_pass_check_evidence_rejects_contradictory_acceptance_observations():
    schema = json.loads((PLUGIN_ROOT / "schemas" / "check-evidence.schema.json").read_text(encoding="utf-8"))
    example = json.loads((PLUGIN_ROOT / "examples" / "check-evidence.example.json").read_text(encoding="utf-8"))
    for contradictory_value in (False, "false", 0):
        example["observations"].append(
            {
                "name": "acceptance",
                "value": contradictory_value,
                "source": "anonymous-conflicting-fixture",
            }
        )
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(example, schema)
        example["observations"].pop()


def test_every_required_route_check_has_one_evidence_type_contract():
    schema = json.loads((PLUGIN_ROOT / "schemas" / "check-evidence.schema.json").read_text(encoding="utf-8"))
    contracted_ids: list[str] = []
    for condition in schema["allOf"]:
        evidence_type = condition.get("then", {}).get("properties", {}).get("evidence_type", {}).get("const")
        if evidence_type is None:
            continue
        check_id = condition["if"]["properties"]["check_id"]
        contracted_ids.extend(check_id.get("enum", [check_id.get("const")]))

    required_ids = {
        check_id for route_checks in REQUIRED_CHECK_STAGES.values() for check_id in route_checks
    }
    assert set(contracted_ids) == required_ids
    assert len(contracted_ids) == len(set(contracted_ids))

    schema_types = {}
    for condition in schema["allOf"]:
        evidence_type = condition.get("then", {}).get("properties", {}).get("evidence_type", {}).get("const")
        if evidence_type is None:
            continue
        check_id = condition["if"]["properties"]["check_id"]
        for contracted_id in check_id.get("enum", [check_id.get("const")]):
            schema_types[contracted_id] = evidence_type
    catalog_types = {
        check_id: evidence_type
        for route_types in REQUIRED_CHECK_EVIDENCE_TYPES.values()
        for check_id, evidence_type in route_types.items()
    }
    assert schema_types == catalog_types


def test_route_plan_rejects_empty_dependency_action_object():
    schema = json.loads((PLUGIN_ROOT / "schemas" / "route-plan.schema.json").read_text(encoding="utf-8"))
    example = json.loads((PLUGIN_ROOT / "examples" / "route-plan.example.json").read_text(encoding="utf-8"))
    example["steps"][0]["step_id"] = "SRC2UE427.CLASSIFY_DEPS"
    example["steps"][0]["assets"] = [{}]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(example, schema)


def test_package_pass_requires_l5_not_l4():
    schema = json.loads((PLUGIN_ROOT / "schemas" / "verified-run.schema.json").read_text(encoding="utf-8"))
    example = json.loads((PLUGIN_ROOT / "examples" / "verified-run.example.json").read_text(encoding="utf-8"))
    required_ids = [
        "source_handoff_passed",
        "build_target_os_match",
        "package_config_valid",
        "cook_dependencies_complete",
        "package_artifact_hashed",
        "archive_safety_passed",
        "target_backup_complete",
        "package_registry_visible",
        "load_world_stable",
        "source_visual_parity",
        "road_collision_smoke",
        "opendrive_spawn_expected",
        "dynamic_smoke",
        "rollback_ready",
    ]
    example.update(
        {
            "route": "source-carla-to-package-carla",
            "status": "PASS",
            "evidence_level": "L4",
            "environment": {
                "host_os": "anonymous-linux",
                "platform": "linux-x86_64",
                "source_carla_version": "0.9.16",
                "source_ue_version": "4.26.2-carla-fork",
                "target_carla_version": "0.9.16",
            },
            "input_hashes": [{"path": "input.json", "sha256": "a" * 64}],
            "target_identity": {
                "package_version": "0.9.16",
                "package_fingerprint": "anonymous",
                "map_mode": "standard",
            },
            "claims_evaluated": ["C-SRC-PKG-001"],
            "required_checks": [
                {"id": check_id, "required": True, "status": "PASS", "evidence": ["stage.json"]}
                for check_id in required_ids
            ],
            "stage_results": ["stage.json"],
            "protected_property_diff": {"status": "PASS"},
            "artifacts": [{"path": "stage.json", "sha256": "b" * 64, "kind": "stage-result"}],
            "redaction": {"status": "PASS", "report": "redaction.json"},
        }
    )
    example["signoff"].update(
        {"runner": "maintainer", "reviewer": "reviewer", "date": "2026-08-26", "evidence_sha256": "b" * 64}
    )
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(example, schema)


@pytest.mark.parametrize(
    ("statuses", "overall_status"),
    [
        (["NOT_APPLICABLE"], "INCOMPLETE"),
        (["FAIL", "NOT_RUN"], "FAIL"),
        (["FAIL", "BLOCKED"], "FAIL"),
    ],
)
def test_verified_run_schema_matches_required_check_aggregation(statuses, overall_status):
    schema = json.loads((PLUGIN_ROOT / "schemas" / "verified-run.schema.json").read_text(encoding="utf-8"))
    example = json.loads((PLUGIN_ROOT / "examples" / "verified-run.example.json").read_text(encoding="utf-8"))
    example["status"] = overall_status
    example["required_checks"] = [
        {"id": f"check-{index}", "required": True, "status": status, "evidence": []}
        for index, status in enumerate(statuses)
    ]
    jsonschema.validate(example, schema)


@pytest.mark.parametrize("incorrect_status", ["INCOMPLETE", "BLOCKED"])
def test_verified_run_schema_rejects_rollup_that_hides_required_fail(incorrect_status):
    schema = json.loads((PLUGIN_ROOT / "schemas" / "verified-run.schema.json").read_text(encoding="utf-8"))
    example = json.loads((PLUGIN_ROOT / "examples" / "verified-run.example.json").read_text(encoding="utf-8"))
    example["status"] = incorrect_status
    example["required_checks"] = [
        {"id": "failed", "required": True, "status": "FAIL", "evidence": []},
        {
            "id": "other",
            "required": True,
            "status": "NOT_RUN" if incorrect_status == "INCOMPLETE" else "BLOCKED",
            "evidence": [],
        },
    ]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(example, schema)


def test_verified_run_accepts_complete_source_to_ue427_pass_contract():
    schema = json.loads((PLUGIN_ROOT / "schemas" / "verified-run.schema.json").read_text(encoding="utf-8"))
    example = json.loads((PLUGIN_ROOT / "examples" / "verified-run.example.json").read_text(encoding="utf-8"))
    required_ids = [
        "source_asset_inventory_complete",
        "dependency_classification_complete",
        "unreal_safe_migration",
        "target_engine_version_recorded",
        "required_assets_present",
        "missing_assets_zero",
        "required_materials_valid",
        "disallowed_carla_refs_zero",
        "runtime_objects_have_strategy",
        "world_settings_environment_lighting",
        "road_collision_smoke",
        "target_reopen",
        "pie_smoke",
        "second_clean_project_cold_copy",
        "ue427_handoff_complete",
    ]
    example.update(
        {
            "status": "PASS",
            "evidence_level": "L5",
            "environment": {
                "host_os": "anonymous-linux",
                "platform": "linux-x86_64",
                "source_carla_version": "0.9.16",
                "source_ue_version": "4.26.2-carla-fork",
                "target_ue_version": "4.27.2",
            },
            "input_hashes": [{"path": "inputs/manifest.json", "sha256": "a" * 64}],
            "target_identity": {
                "engine_version": "4.27.2",
                "project_fingerprint": "anonymous-target",
                "map_mode": "standard",
            },
            "required_checks": [
                {"id": check_id, "required": True, "status": "PASS", "evidence": [f"checks/{check_id}.json"]}
                for check_id in required_ids
            ],
            "stage_results": ["stages/migrate.json"],
            "protected_property_diff": {"status": "PASS"},
            "artifacts": [
                {"path": "checks/cold-copy.json", "sha256": "b" * 64, "kind": "stage-result"}
            ],
            "redaction": {"status": "PASS", "report": "redaction-report.json"},
        }
    )
    example["signoff"].update(
        {
            "runner": "maintainer",
            "reviewer": "reviewer",
            "date": "2026-08-26",
            "evidence_sha256": "c" * 64,
        }
    )
    jsonschema.validate(example, schema)


def test_schema_catalog_is_exactly_the_shared_contract():
    actual = {path.stem.removesuffix(".schema") for path in (PLUGIN_ROOT / "schemas").glob("*.schema.json")}
    assert actual == SCHEMA_NAMES


@pytest.mark.parametrize(
    "route",
    ["roadrunner-to-source-carla", "source-carla-to-package-carla", "source-carla-to-ue427"],
)
def test_core_outputs_conform_to_public_contracts(route: str, workspace_factory):
    workspace = workspace_factory(route)
    schemas = {
        name: json.loads((PLUGIN_ROOT / "schemas" / f"{name}.schema.json").read_text(encoding="utf-8"))
        for name in ("map-workspace", "stage-result", "route-plan", "validation-report")
    }
    inspection = inspect_workspace(workspace, route)
    plan = build_plan(workspace, route, inspection)
    report = pending_validation_report(workspace, route)
    jsonschema.validate(workspace, schemas["map-workspace"])
    jsonschema.validate(inspection, schemas["stage-result"])
    jsonschema.validate(plan, schemas["route-plan"])
    jsonschema.validate(report, schemas["validation-report"])
