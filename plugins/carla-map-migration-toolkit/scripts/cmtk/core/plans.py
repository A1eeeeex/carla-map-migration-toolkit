from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from .errors import CmtkError
from .hashing import sha256_file, sha256_json
from .paths import require_within_roots

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


def _hashable_plan(plan: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in plan.items() if key != "plan_sha256"}


def seal_plan(plan: dict[str, Any]) -> dict[str, Any]:
    sealed = deepcopy(plan)
    sealed.pop("plan_sha256", None)
    sealed["plan_sha256"] = sha256_json(sealed)
    return sealed


def verify_plan(plan: dict[str, Any], *, expected_sha256: str | None = None) -> None:
    actual = sha256_json(_hashable_plan(plan))
    recorded = plan.get("plan_sha256")
    if not recorded or actual != recorded or (expected_sha256 is not None and actual != expected_sha256):
        raise CmtkError(
            "PLAN-HASH-MISMATCH",
            "The route plan hash does not match its content or requested hash.",
            details={"recorded": recorded, "actual": actual, "expected": expected_sha256},
        )
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
