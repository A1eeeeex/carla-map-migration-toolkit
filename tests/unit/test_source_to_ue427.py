from __future__ import annotations

import json
from pathlib import Path

import pytest
from cmtk.core.errors import CmtkError
from cmtk.core.plans import verify_plan
from cmtk.routes.inspection import inspect_workspace
from cmtk.routes.planning import build_plan
from cmtk.routes.source_to_ue427 import classify_dependencies
from conftest import REPO_ROOT


def _dependency(source_object: str, classification: str, **overrides) -> dict:
    value = {
        "source_object": source_object,
        "classification": classification,
        "target_strategy": "migrate-with-unreal-assettools",
        "referencers": ["/Game/Maps/Example/Example"],
        "migration_action": "Migrate the reviewed dependency closure through Source Unreal Editor.",
        "verification": ["Rescan the target Asset Registry."],
        "rollback": ["Restore objects listed by the backup manifest."],
        "residual_risk": "Target Editor replay is still required.",
    }
    value.update(overrides)
    return value


def test_dependency_classification_preserves_complete_action_contract():
    result = classify_dependencies(
        {
            "dependencies": [
                _dependency("/Game/Maps/Example/Road", "portable"),
                _dependency(
                    "/Game/Carla/Blueprints/Weather",
                    "replaceable",
                    target_strategy="replace-with-local-environment-blueprint",
                ),
            ]
        }
    )
    assert result["status"] == "PASS"
    assert result["blocked_reasons"] == []
    assert result["counts"] == {"portable": 1, "replaceable": 1}
    assert set(result["dependencies"][0]) == {
        "source_object",
        "classification",
        "target_strategy",
        "referencers",
        "migration_action",
        "verification",
        "rollback",
        "residual_risk",
    }


def test_empty_dependency_manifest_is_not_complete_classification():
    result = classify_dependencies({"dependencies": []})
    assert result["status"] == "BLOCKED"
    assert result["blocked_reasons"] == ["UE427-DEPENDENCY-MANIFEST-EMPTY"]


@pytest.mark.parametrize("classification", [[], {}])
def test_non_scalar_dependency_classification_is_structured_unknown(classification):
    result = classify_dependencies(
        {"dependencies": [_dependency("/Game/Maps/Example/Malformed", classification)]}
    )
    assert result["status"] == "BLOCKED"
    assert "UE427-DEPENDENCY-UNKNOWN" in result["blocked_reasons"]


@pytest.mark.parametrize(
    ("dependency", "reason_code"),
    [
        (_dependency("/Game/Maps/Example/Unknown", "unknown"), "UE427-DEPENDENCY-UNKNOWN"),
        (_dependency("/Game/Maps/Example/Blocked", "blocked"), "UE427-DEPENDENCY-BLOCKED"),
        (
            _dependency("/Game/Carla/Blueprints/GameMode", "replaceable", target_strategy=None),
            "UE427-REPLACEMENT-UNDEFINED",
        ),
        (
            _dependency("/Game/Maps/Example/NoStrategy", "portable", target_strategy=None),
            "UE427-DEPENDENCY-UNKNOWN",
        ),
    ],
)
def test_unknown_blocked_or_undefined_dependency_blocks_execution(dependency: dict, reason_code: str):
    result = classify_dependencies({"dependencies": [dependency]})
    assert result["status"] == "BLOCKED"
    assert reason_code in result["blocked_reasons"]


def test_source_to_ue427_plan_embeds_classification_and_refuses_unknown(workspace_factory):
    workspace = workspace_factory("source-carla-to-ue427")
    manifest_path = Path(workspace["input"]["dependency_manifest_path"])
    manifest_path.write_text(
        json.dumps({"dependencies": [_dependency("/Game/Maps/Example/Unknown", "unknown")]}),
        encoding="utf-8",
    )
    inspection = inspect_workspace(workspace, "source-carla-to-ue427")
    dependency_check = next(check for check in inspection["checks"] if check["id"] == "UE427-DEPENDENCY-CLASSIFICATION")
    assert dependency_check["status"] == "BLOCKED"
    plan = build_plan(workspace, "source-carla-to-ue427", inspection)
    classify_step = next(step for step in plan["steps"] if step["step_id"] == "SRC2UE427.CLASSIFY_DEPS")

    assert classify_step["assets"][0]["classification"] == "unknown"
    assert "UE427-DEPENDENCY-UNKNOWN" in plan["blocked_reasons"]
    with pytest.raises(CmtkError) as error:
        verify_plan(plan)
    assert error.value.reason_code == "PLAN-BLOCKED"


@pytest.mark.parametrize(
    ("fixture_name", "expected_status"),
    [("valid.json", "PASS"), ("blocked.json", "BLOCKED")],
)
def test_anonymous_dependency_fixture_classification(fixture_name: str, expected_status: str):
    path = REPO_ROOT / "tests" / "fixtures" / "source-to-ue427-dependencies" / fixture_name
    result = classify_dependencies(json.loads(path.read_text(encoding="utf-8")))
    assert result["status"] == expected_status


def test_dependency_manifest_root_must_be_inside_workspace_allowed_roots(workspace_factory, tmp_path: Path):
    workspace = workspace_factory("source-carla-to-ue427")
    outside_root = tmp_path / "outside-source-input"
    outside_root.mkdir()
    manifest_path = outside_root / "source-dependency-manifest.json"
    manifest_path.write_text('{"dependencies": []}\n', encoding="utf-8")
    workspace["input"]["root"] = str(outside_root)
    workspace["input"]["dependency_manifest_path"] = str(manifest_path)

    inspection = inspect_workspace(workspace, "source-carla-to-ue427")
    dependency_check = next(check for check in inspection["checks"] if check["id"] == "UE427-DEPENDENCY-CLASSIFICATION")
    assert dependency_check["status"] == "BLOCKED"
    assert dependency_check["reason_code"] == "PATH-OUTSIDE-ALLOWED-ROOT"
