from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from cmtk.core.errors import CmtkError
from cmtk.core.jsonio import load_json
from cmtk.core.paths import require_within_roots

DEPENDENCY_CLASSES = {"portable", "localizable", "replaceable", "remove", "blocked", "unknown"}


def _string_list(value: Any) -> list[str] | None:
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        return None
    return value


def classify_dependencies(manifest: dict[str, Any]) -> dict[str, Any]:
    raw_dependencies = manifest.get("dependencies") if isinstance(manifest, dict) else None
    if not isinstance(raw_dependencies, list) or not all(isinstance(item, dict) for item in raw_dependencies):
        raise CmtkError(
            "UE427-DEPENDENCY-MANIFEST-INVALID",
            "Source dependency manifest must contain an array of dependency objects.",
        )

    dependencies: list[dict[str, Any]] = []
    blocked_reasons: set[str] = set()
    if not raw_dependencies:
        blocked_reasons.add("UE427-DEPENDENCY-MANIFEST-EMPTY")
    seen: set[str] = set()
    for raw in raw_dependencies:
        source_object = raw.get("source_object")
        classification = raw.get("classification")
        target_strategy = raw.get("target_strategy")
        referencers = _string_list(raw.get("referencers"))
        migration_action = raw.get("migration_action")
        verification = _string_list(raw.get("verification"))
        rollback = _string_list(raw.get("rollback"))
        residual_risk = raw.get("residual_risk")

        if not isinstance(classification, str) or classification not in DEPENDENCY_CLASSES:
            classification = "unknown"
            blocked_reasons.add("UE427-DEPENDENCY-UNKNOWN")
        if classification == "unknown":
            blocked_reasons.add("UE427-DEPENDENCY-UNKNOWN")
        elif classification == "blocked":
            blocked_reasons.add("UE427-DEPENDENCY-BLOCKED")
        elif classification == "replaceable" and not target_strategy:
            blocked_reasons.add("UE427-REPLACEMENT-UNDEFINED")

        contract_incomplete = (
            not isinstance(source_object, str)
            or not source_object
            or source_object in seen
            or (
                classification not in {"blocked", "unknown"}
                and (not isinstance(target_strategy, str) or not target_strategy)
            )
            or referencers is None
            or not isinstance(migration_action, str)
            or not migration_action
            or verification is None
            or not verification
            or rollback is None
            or not rollback
            or not isinstance(residual_risk, str)
            or not residual_risk
        )
        if contract_incomplete:
            blocked_reasons.add("UE427-DEPENDENCY-UNKNOWN")
        if isinstance(source_object, str) and source_object:
            seen.add(source_object)

        dependencies.append(
            {
                "source_object": source_object,
                "classification": classification,
                "target_strategy": target_strategy,
                "referencers": referencers or [],
                "migration_action": migration_action,
                "verification": verification or [],
                "rollback": rollback or [],
                "residual_risk": residual_risk,
            }
        )

    return {
        "schema_version": "1.0.0",
        "status": "BLOCKED" if blocked_reasons else "PASS",
        "counts": dict(sorted(Counter(item["classification"] for item in dependencies).items())),
        "dependencies": dependencies,
        "blocked_reasons": sorted(blocked_reasons),
    }


def classify_workspace_dependencies(workspace: dict[str, Any]) -> dict[str, Any]:
    input_root = require_within_roots(
        workspace["input"]["root"],
        workspace["execution"]["allowed_roots"],
    )
    manifest_path = require_within_roots(
        workspace["input"]["dependency_manifest_path"],
        [input_root],
    )
    return classify_dependencies(load_json(manifest_path))


def classify_dependency_manifest_bytes(content: bytes, source: str | Path) -> dict[str, Any]:
    try:
        manifest = json.loads(content)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise CmtkError(
            "INPUT-JSON-INVALID",
            "Unable to read valid JSON input.",
            details={"path": str(source), "error": str(error)},
        ) from error
    return classify_dependencies(manifest)
