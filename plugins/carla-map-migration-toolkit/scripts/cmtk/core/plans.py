from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from typing import Any

import jsonschema

from .errors import CmtkError
from .hashing import sha256_file, sha256_json
from .jsonio import load_json
from .paths import canonical_path, require_within_roots

_REQUIRED_INPUT_KINDS = {
    "roadrunner-to-source-carla": {"route-input", "opendrive"},
    "source-carla-to-package-carla": {
        "map-handoff",
        "source-asset-inventory",
        "source-dependency-manifest",
        "route-input-manifest",
        "opendrive",
    },
    "source-carla-to-ue427": {
        "map-handoff",
        "source-asset-inventory",
        "source-dependency-manifest",
        "route-input-manifest",
        "opendrive",
    },
}
ROUTE_PLAN_SCHEMA_VERSION = "1.5.0"
_ROUTE_PLAN_SCHEMA_PATH = Path(__file__).resolve().parents[3] / "schemas" / "route-plan.schema.json"


def _hashable_plan(plan: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in plan.items() if key != "plan_sha256"}


def seal_plan(plan: dict[str, Any]) -> dict[str, Any]:
    sealed = deepcopy(plan)
    sealed.pop("plan_sha256", None)
    sealed["plan_sha256"] = sha256_json(sealed)
    return sealed


@lru_cache(maxsize=1)
def _route_plan_schema() -> dict[str, Any]:
    schema = load_json(_ROUTE_PLAN_SCHEMA_PATH)
    if not isinstance(schema, dict):
        raise CmtkError("PLAN-INVALID", "Route-plan schema must be a JSON object.")
    return schema


def _verify_route_plan_schema(plan: dict[str, Any]) -> None:
    errors = list(jsonschema.Draft202012Validator(_route_plan_schema()).iter_errors(plan))
    if errors:
        raise CmtkError(
            "PLAN-INVALID",
            "Route plan does not satisfy the current schema.",
            details={"validation_message": errors[0].message},
        )


def _verify_unblocked_dependency_actions(plan: dict[str, Any]) -> None:
    if plan.get("blocked_reasons") or plan.get("route") != "source-carla-to-ue427":
        return
    classify_steps = [
        step for step in plan.get("steps", []) if step.get("step_id") == "SRC2UE427.CLASSIFY_DEPS"
    ]
    if not classify_steps:
        return
    if len(classify_steps) != 1:
        raise CmtkError("PLAN-INVALID", "Route plan must contain at most one dependency-classification step.")
    from cmtk.routes.source_to_ue427 import classify_dependencies

    result = classify_dependencies({"dependencies": classify_steps[0]["assets"]})
    if result["status"] != "PASS":
        raise CmtkError(
            "PLAN-INVALID",
            "Unblocked route plan contains an incomplete dependency action.",
            details={"blocked_reasons": result["blocked_reasons"]},
        )


def _verify_route_steps(plan: dict[str, Any]) -> None:
    from cmtk.routes.catalog import ROUTES, STEP_CATALOG

    route = plan["route"]
    prefix = ROUTES[route]["prefix"]
    expected_ids = [f"{prefix}.{suffix}" for suffix, _step_type, _context, _risk in STEP_CATALOG[route]]
    actual_ids = [step["step_id"] for step in plan["steps"]]
    if actual_ids != expected_ids:
        raise CmtkError(
            "PLAN-INVALID",
            "Route plan steps must exactly match the ordered route-stage contract.",
            details={"expected": expected_ids, "actual": actual_ids},
        )
    for step, (suffix, expected_type, expected_context, expected_risk) in zip(
        plan["steps"], STEP_CATALOG[route], strict=True
    ):
        expected_id = f"{prefix}.{suffix}"
        type_matches = step["type"] == expected_type or (
            expected_id == "SRC2UE427.CLASSIFY_DEPS"
            and step["type"] == "BLOCKED"
            and bool(plan.get("blocked_reasons"))
        )
        if not type_matches or (step["execution_context"], step["risk"]) != (
            expected_context,
            expected_risk,
        ):
            raise CmtkError(
                "PLAN-INVALID",
                "Route stage safety metadata does not match the route catalog.",
                details={
                    "step_id": expected_id,
                    "expected": {
                        "type": expected_type,
                        "execution_context": expected_context,
                        "risk": expected_risk,
                    },
                    "actual": {
                        "type": step["type"],
                        "execution_context": step["execution_context"],
                        "risk": step["risk"],
                    },
                },
            )


def _verify_plan_path_syntax(plan: dict[str, Any]) -> None:
    for step in plan["steps"]:
        for field in ("read_paths", "write_paths"):
            for path in step[field]:
                canonical_path(path)
        backup_root = step["backup"].get("root")
        if backup_root is not None:
            canonical_path(backup_root)


def _verify_workspace_step_paths(plan: dict[str, Any], workspace: dict[str, Any]) -> None:
    from cmtk.routes.planning import route_step_path_contract

    expected = route_step_path_contract(workspace, plan["route"])
    actual = {
        step["step_id"]: {
            "read_paths": step["read_paths"],
            "write_paths": step["write_paths"],
            "backup": step["backup"],
        }
        for step in plan["steps"]
    }
    if actual != expected:
        raise CmtkError(
            "PLAN-INVALID",
            "Route stage paths do not match the fingerprinted workspace contract.",
            details={"expected": expected, "actual": actual},
        )


def verify_plan(plan: dict[str, Any], *, expected_sha256: str | None = None) -> None:
    if plan.get("schema_version") != ROUTE_PLAN_SCHEMA_VERSION:
        raise CmtkError(
            "SCHEMA-VERSION-UNSUPPORTED",
            "Route plan must be regenerated with the current schema version.",
            details={"expected": ROUTE_PLAN_SCHEMA_VERSION, "actual": plan.get("schema_version")},
        )
    _verify_route_plan_schema(plan)
    actual = sha256_json(_hashable_plan(plan))
    recorded = plan.get("plan_sha256")
    if not recorded or actual != recorded or (expected_sha256 is not None and actual != expected_sha256):
        raise CmtkError(
            "PLAN-HASH-MISMATCH",
            "The route plan hash does not match its content or requested hash.",
            details={"recorded": recorded, "actual": actual, "expected": expected_sha256},
        )
    _verify_route_steps(plan)
    _verify_plan_path_syntax(plan)
    _verify_unblocked_dependency_actions(plan)
    if plan.get("blocked_reasons"):
        raise CmtkError(
            "PLAN-BLOCKED",
            "The route plan contains unresolved blockers and is not executable.",
            details={"blocked_reasons": plan["blocked_reasons"]},
        )


def verify_workspace_fingerprint(plan: dict[str, Any], workspace: dict[str, Any]) -> None:
    if plan.get("route") != workspace.get("route"):
        raise CmtkError(
            "ROUTE-CONFLICT",
            "The route plan and workspace declare different routes.",
            details={"plan_route": plan.get("route"), "workspace_route": workspace.get("route")},
        )
    actual = sha256_json(workspace)
    if plan.get("workspace_sha256") != actual:
        raise CmtkError(
            "PLAN-STALE",
            "The workspace changed after the plan was created.",
            details={"planned": plan.get("workspace_sha256"), "actual": actual},
        )
    _verify_workspace_step_paths(plan, workspace)


def verify_input_fingerprints(plan: dict[str, Any], allowed_roots: list[str]) -> None:
    required_kinds = _REQUIRED_INPUT_KINDS.get(plan.get("route"), set())
    actual_kinds = {
        fingerprint.get("kind") for fingerprint in plan.get("input_fingerprints", []) if isinstance(fingerprint, dict)
    }
    missing_kinds = sorted(required_kinds - actual_kinds)
    if missing_kinds:
        raise CmtkError(
            "PLAN-INPUT-FINGERPRINTS-INCOMPLETE",
            "The route plan does not fingerprint every required input class.",
            details={"missing_kinds": missing_kinds},
        )
    stale: list[dict[str, Any]] = []
    for fingerprint in plan.get("input_fingerprints", []):
        raw_path = fingerprint.get("path")
        if not raw_path:
            stale.append({"name": fingerprint.get("name"), "reason": "missing planned path"})
            continue
        path = require_within_roots(raw_path, allowed_roots)
        if not path.is_file():
            stale.append({"name": Path(raw_path).name, "reason": "input missing"})
            continue
        actual_size = path.stat().st_size
        actual_hash = sha256_file(path)
        if actual_size != fingerprint.get("size_bytes") or actual_hash != fingerprint.get("sha256"):
            stale.append(
                {
                    "name": path.name,
                    "reason": "size or SHA-256 changed",
                    "planned_size_bytes": fingerprint.get("size_bytes"),
                    "actual_size_bytes": actual_size,
                    "planned_sha256": fingerprint.get("sha256"),
                    "actual_sha256": actual_hash,
                }
            )
    if stale:
        raise CmtkError(
            "PLAN-STALE",
            "One or more route inputs changed after the plan was created.",
            details={"inputs": stale},
        )
