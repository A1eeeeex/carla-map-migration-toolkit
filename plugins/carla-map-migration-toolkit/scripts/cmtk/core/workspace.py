from __future__ import annotations

from typing import Any

from .errors import CmtkError

_COMMON_OBJECT_FIELDS = {
    "map": {"id", "name", "mode"},
    "source_carla": {"root", "version", "branch", "commit", "engine_version", "platform", "map_asset_path"},
    "execution": {"mode", "backup_root", "artifact_root", "allow_replace_existing", "allowed_roots"},
}
_ROUTE_OBJECT_FIELDS = {
    "roadrunner-to-source-carla": {"input": {"profile", "root"}},
    "source-carla-to-package-carla": {
        "input": {
            "profile",
            "root",
            "handoff_path",
            "asset_inventory_path",
            "dependency_manifest_path",
            "route_manifest_path",
        },
        "package_carla": {"root", "version", "platform", "profile"},
    },
    "source-carla-to-ue427": {
        "input": {
            "profile",
            "root",
            "handoff_path",
            "asset_inventory_path",
            "dependency_manifest_path",
            "route_manifest_path",
        },
        "ue427": {"engine_root", "engine_version", "uproject", "map_asset_path", "profile", "cold_copy_uproject"},
    },
}


def validate_workspace_shape(workspace: dict[str, Any], route: str | None = None) -> None:
    selected_route = route or workspace.get("route")
    missing: list[str] = []
    invalid: list[str] = []
    for field in ("schema_version", "workspace_id", "route"):
        if field not in workspace:
            missing.append(field)
    if selected_route not in _ROUTE_OBJECT_FIELDS:
        invalid.append("route")

    required_objects = dict(_COMMON_OBJECT_FIELDS)
    if selected_route in _ROUTE_OBJECT_FIELDS:
        required_objects.update(_ROUTE_OBJECT_FIELDS[selected_route])
    for object_name, fields in required_objects.items():
        value = workspace.get(object_name)
        if not isinstance(value, dict):
            if object_name not in workspace:
                missing.append(object_name)
            else:
                invalid.append(object_name)
            continue
        missing.extend(f"{object_name}.{field}" for field in sorted(fields - value.keys()))

    execution = workspace.get("execution")
    if isinstance(execution, dict) and not isinstance(execution.get("allowed_roots"), list):
        invalid.append("execution.allowed_roots")
    if missing or invalid:
        raise CmtkError(
            "WORKSPACE-INVALID",
            "Workspace is missing required fields or contains invalid object shapes.",
            details={"missing": sorted(missing), "invalid": sorted(invalid)},
        )
