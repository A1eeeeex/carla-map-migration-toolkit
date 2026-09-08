from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from cmtk.core.errors import CmtkError
from cmtk.core.hashing import sha256_bytes, sha256_json
from cmtk.core.paths import require_within_roots
from cmtk.core.plans import ROUTE_PLAN_SCHEMA_VERSION, seal_plan

from .catalog import ROUTES, STEP_CATALOG
from .source_to_ue427 import classify_dependency_manifest_bytes


def _timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _input_snapshots(workspace: dict[str, Any], route: str) -> tuple[list[dict[str, Any]], dict[Path, bytes]]:
    allowed_roots = workspace["execution"]["allowed_roots"]
    candidates: dict[Path, str] = {}
    if route == "roadrunner-to-source-carla":
        export_root = require_within_roots(workspace["input"]["root"], allowed_roots)
        patterns = {
            "roadrunner-datasmith": ("*.udatasmith", "*.xodr"),
            "roadrunner-filmbox": ("*.fbx", "*.rrdata.xml", "*.xodr"),
            "generic-fbx-xodr": ("*.fbx", "*.xodr"),
        }.get(workspace["input"]["profile"], ())
        for pattern in patterns:
            for path in export_root.glob(pattern):
                if path.is_file():
                    candidates[require_within_roots(path, [export_root])] = "route-input"
    else:
        source_input = workspace["input"]
        source_input_root = require_within_roots(source_input["root"], allowed_roots)
        manifest_kinds = {
            "handoff_path": "map-handoff",
            "asset_inventory_path": "source-asset-inventory",
            "dependency_manifest_path": "source-dependency-manifest",
            "route_manifest_path": "route-input-manifest",
        }
        for field, kind in manifest_kinds.items():
            raw_path = source_input.get(field)
            if not raw_path:
                continue
            path = require_within_roots(raw_path, [source_input_root])
            if path.is_file():
                candidates[path] = kind
    xodr = workspace["source_carla"].get("xodr_path")
    if xodr:
        path = require_within_roots(xodr, allowed_roots)
        if path.is_file():
            candidates[path] = "opendrive"
    snapshots: dict[Path, bytes] = {}
    for path in sorted(candidates, key=str):
        try:
            snapshots[path] = path.read_bytes()
        except OSError as error:
            raise CmtkError(
                "PATH-TARGET-NOT-FOUND",
                "Unable to capture a stable route input snapshot.",
                details={"path": str(path), "error": str(error)},
            ) from error
    fingerprints = [
        {
            "kind": kind,
            "name": path.name,
            "path": str(path),
            "size_bytes": len(snapshots[path]),
            "sha256": sha256_bytes(snapshots[path]),
        }
        for path, kind in sorted(candidates.items(), key=lambda item: str(item[0]))
    ]
    return fingerprints, snapshots


def _environment_fingerprints(workspace: dict[str, Any], route: str) -> list[dict[str, Any]]:
    source = workspace["source_carla"]
    values = [
        {
            "component": "source_carla",
            "version": source.get("version"),
            "engine": source.get("engine_version"),
            "platform": source.get("platform"),
            "commit": source.get("commit"),
        }
    ]
    if route == "source-carla-to-package-carla":
        package = workspace["package_carla"]
        values.append(
            {
                "component": "package_carla",
                "version": package.get("version"),
                "platform": package.get("platform"),
                "profile": package.get("profile"),
            }
        )
    elif route == "source-carla-to-ue427":
        ue427 = workspace["ue427"]
        values.append(
            {
                "component": "ue427",
                "engine": ue427.get("engine_version"),
                "profile": ue427.get("profile"),
            }
        )
    return values


def _resolved_path(workspace: dict[str, Any], value: str) -> str:
    return str(require_within_roots(value, workspace["execution"]["allowed_roots"]))


def _route_read_paths(workspace: dict[str, Any], route: str) -> list[str]:
    source = workspace["source_carla"]
    values = [source["root"]]
    if source.get("xodr_path"):
        values.append(source["xodr_path"])
    if route == "roadrunner-to-source-carla":
        values.append(workspace["input"]["root"])
    elif route == "source-carla-to-package-carla":
        values.append(workspace["package_carla"]["root"])
    else:
        ue427 = workspace["ue427"]
        values.extend(
            [ue427["engine_root"], str(Path(ue427["uproject"]).parent), str(Path(ue427["cold_copy_uproject"]).parent)]
        )
    return sorted({_resolved_path(workspace, value) for value in values})


def _step_write_paths(workspace: dict[str, Any], route: str, suffix: str) -> list[str]:
    execution = workspace["execution"]
    if suffix == "HANDOFF":
        return [_resolved_path(workspace, execution["artifact_root"])]
    if route == "roadrunner-to-source-carla":
        if suffix in {"PREPARE_TARGET", "IMPORT", "REPAIR", "OPTIMIZE"}:
            return [_resolved_path(workspace, workspace["source_carla"]["root"])]
        return []
    if route == "source-carla-to-package-carla":
        if suffix in {"REPAIR", "BUILD", "OPTIMIZE"}:
            return [
                _resolved_path(workspace, workspace["source_carla"]["root"]),
                _resolved_path(workspace, execution["artifact_root"]),
            ]
        if suffix == "BACKUP_TARGET":
            return [_resolved_path(workspace, execution["backup_root"])]
        if suffix == "IMPORT":
            return [_resolved_path(workspace, workspace["package_carla"]["root"])]
        return []
    ue427 = workspace["ue427"]
    if suffix == "COLD_COPY":
        return [_resolved_path(workspace, str(Path(ue427["cold_copy_uproject"]).parent))]
    if suffix == "MIGRATE_ASSETS":
        return [
            _resolved_path(workspace, workspace["source_carla"]["root"]),
            _resolved_path(workspace, str(Path(ue427["uproject"]).parent)),
        ]
    if suffix in {
        "CREATE_TARGET",
        "REPAIR_MATERIALS",
        "REPLACE_CARLA",
        "REPAIR_WORLD",
        "REPAIR_COLLISION",
        "CLEAN_REFS",
        "OPTIMIZE",
    }:
        return [_resolved_path(workspace, str(Path(ue427["uproject"]).parent))]
    return []


def route_step_path_contract(workspace: dict[str, Any], route: str) -> dict[str, dict[str, Any]]:
    prefix = ROUTES[route]["prefix"]
    read_paths = _route_read_paths(workspace, route)
    backup_root = _resolved_path(workspace, workspace["execution"]["backup_root"])
    contract: dict[str, dict[str, Any]] = {}
    for suffix, _step_type, _context, _risk in STEP_CATALOG[route]:
        write_paths = _step_write_paths(workspace, route, suffix)
        backup_required = bool(write_paths and suffix != "HANDOFF")
        contract[f"{prefix}.{suffix}"] = {
            "read_paths": read_paths,
            "write_paths": write_paths,
            "backup": {} if not backup_required else {"root": backup_root, "required": True},
        }
    return contract


def build_plan(workspace: dict[str, Any], route: str, inspection: dict[str, Any]) -> dict[str, Any]:
    prefix = ROUTES[route]["prefix"]
    execution = workspace["execution"]
    path_contract = route_step_path_contract(workspace, route)
    input_fingerprints, input_snapshots = _input_snapshots(workspace, route)
    dependency_result = None
    if route == "source-carla-to-ue427":
        dependency_path = require_within_roots(
            workspace["input"]["dependency_manifest_path"],
            [require_within_roots(workspace["input"]["root"], execution["allowed_roots"])],
        )
        dependency_content = input_snapshots.get(dependency_path)
        if dependency_content is None:
            raise CmtkError(
                "UE427-DEPENDENCY-MANIFEST-INVALID",
                "Dependency manifest was not captured in the route input snapshot.",
                details={"path": str(dependency_path)},
            )
        dependency_result = classify_dependency_manifest_bytes(dependency_content, dependency_path)

    steps = []
    for suffix, step_type, context, risk in STEP_CATALOG[route]:
        step_id = f"{prefix}.{suffix}"
        step_paths = path_contract[step_id]
        writes = step_paths["write_paths"]
        backup_required = bool(writes and suffix != "HANDOFF")
        assets: list[Any] = []
        expected_changes = [] if not writes else ["Changes must be supplied by a reviewed adapter request."]
        if dependency_result is not None and suffix == "CLASSIFY_DEPS":
            assets = dependency_result["dependencies"]
            expected_changes = ["No asset changes; review the complete dependency action contract."]
            if dependency_result["blocked_reasons"]:
                step_type = "BLOCKED"
        steps.append(
            {
                "step_id": step_id,
                "type": step_type,
                "execution_context": context,
                "read_paths": step_paths["read_paths"],
                "write_paths": writes,
                "assets": assets,
                "expected_changes": expected_changes,
                "risk": risk,
                "backup": step_paths["backup"],
                "verify": [f"verify {prefix}.{suffix}"],
                "rollback": [] if not backup_required else ["restore only objects listed by the backup manifest"],
            }
        )
    blocked = [
        item.get("reason_code", item["id"]) for item in inspection["checks"] if item["status"] in {"FAIL", "BLOCKED"}
    ]
    if dependency_result is not None:
        blocked.extend(dependency_result["blocked_reasons"])
    blocked = sorted(set(blocked))
    created_at = _timestamp()
    plan = {
        "schema_version": ROUTE_PLAN_SCHEMA_VERSION,
        "plan_id": f"plan-{workspace['workspace_id']}-{prefix.lower()}",
        "route": route,
        "created_at": created_at,
        "workspace_sha256": sha256_json(workspace),
        "input_fingerprints": input_fingerprints,
        "environment_fingerprints": _environment_fingerprints(workspace, route),
        "steps": steps,
        "blocked_reasons": blocked,
    }
    return seal_plan(plan)
