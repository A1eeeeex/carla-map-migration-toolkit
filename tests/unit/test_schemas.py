from __future__ import annotations

import json

import jsonschema
import pytest
from cmtk.routes.inspection import inspect_workspace
from cmtk.routes.planning import build_plan
from cmtk.validation.reporting import pending_validation_report
from conftest import PLUGIN_ROOT

SCHEMA_NAMES = {
    "map-workspace",
    "route-plan",
    "stage-result",
    "map-handoff",
    "validation-report",
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
