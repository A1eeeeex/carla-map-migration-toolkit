from __future__ import annotations

from pathlib import Path
from typing import Any

from cmtk.core.errors import CmtkError
from cmtk.core.evidence import check, stage_result
from cmtk.core.paths import require_within_roots, validate_allowed_roots

from .catalog import ROUTES
from .source_to_ue427 import classify_workspace_dependencies


def _ue427_dependency_check(workspace: dict[str, Any]) -> dict[str, Any]:
    try:
        result = classify_workspace_dependencies(workspace)
    except CmtkError as error:
        return check(
            "UE427-DEPENDENCY-CLASSIFICATION",
            "BLOCKED",
            error.message,
            category="dependency",
            reason_code=error.reason_code,
        )
    return check(
        "UE427-DEPENDENCY-CLASSIFICATION",
        result["status"],
        "Every dependency has a complete reviewed action contract."
        if result["status"] == "PASS"
        else "Unknown, blocked, duplicate or incomplete dependency actions prevent migration.",
        category="dependency",
        reason_code=result["blocked_reasons"][0] if result["blocked_reasons"] else None,
        evidence=[{"counts": result["counts"], "blocked_reasons": result["blocked_reasons"]}],
    )


def _path_checks(workspace: dict[str, Any]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    execution = workspace.get("execution", {})
    roots = execution.get("allowed_roots", [])
    try:
        validate_allowed_roots(roots)
    except CmtkError as error:
        return [
            check(
                "WORKSPACE-ALLOWED-ROOTS",
                "BLOCKED",
                error.message,
                category="path-safety",
                reason_code=error.reason_code,
            )
        ]

    source_input_root = None
    if workspace.get("input", {}).get("profile") == "source-carla-map":
        try:
            source_input_root = require_within_roots(workspace["input"].get("root"), roots)
        except CmtkError:
            pass

    candidates: list[tuple[str, Any, bool]] = [
        ("input.root", workspace.get("input", {}).get("root"), True),
        ("input.handoff_path", workspace.get("input", {}).get("handoff_path"), True),
        ("input.asset_inventory_path", workspace.get("input", {}).get("asset_inventory_path"), True),
        ("input.dependency_manifest_path", workspace.get("input", {}).get("dependency_manifest_path"), True),
        ("input.route_manifest_path", workspace.get("input", {}).get("route_manifest_path"), True),
        ("source_carla.root", workspace.get("source_carla", {}).get("root"), True),
        ("source_carla.xodr_path", workspace.get("source_carla", {}).get("xodr_path"), True),
        ("package_carla.root", workspace.get("package_carla", {}).get("root"), True),
        ("ue427.engine_root", workspace.get("ue427", {}).get("engine_root"), True),
        ("ue427.uproject", workspace.get("ue427", {}).get("uproject"), True),
        ("ue427.cold_copy_uproject", workspace.get("ue427", {}).get("cold_copy_uproject"), True),
        ("execution.backup_root", execution.get("backup_root"), True),
        ("execution.artifact_root", execution.get("artifact_root"), True),
    ]
    for label, raw_path, should_exist in candidates:
        if raw_path in (None, ""):
            continue
        try:
            containment_roots = (
                [source_input_root]
                if source_input_root is not None and label.startswith("input.") and label != "input.root"
                else roots
            )
            resolved = require_within_roots(raw_path, containment_roots)
            exists = resolved.exists()
            status = "PASS" if exists or not should_exist else "BLOCKED"
            reason = None if exists else "PATH-TARGET-NOT-FOUND"
            checks.append(
                check(
                    f"WORKSPACE-PATH-{label.upper().replace('.', '-')}",
                    status,
                    f"{label} resolved inside an allowed root" + ("." if exists else " but does not exist."),
                    category="path-safety",
                    reason_code=reason,
                    evidence=[{"field": label, "resolved": str(resolved), "exists": exists}],
                )
            )
        except CmtkError as error:
            checks.append(
                check(
                    f"WORKSPACE-PATH-{label.upper().replace('.', '-')}",
                    "BLOCKED",
                    error.message,
                    category="path-safety",
                    reason_code=error.reason_code,
                )
            )
    return checks


def _rr_export_check(workspace: dict[str, Any]) -> dict[str, Any]:
    profile = workspace.get("input", {}).get("profile")
    if profile not in ROUTES["roadrunner-to-source-carla"]["source_profiles"]:
        return check(
            "RR-INPUT-PROFILE",
            "BLOCKED",
            "RoadRunner input profile is unknown.",
            category="input",
            reason_code="RR-INPUT-PROFILE-UNKNOWN",
        )
    root = Path(workspace["input"]["root"])
    names = [path.name.lower() for path in root.iterdir()] if root.is_dir() else []
    has_xodr = any(name.endswith(".xodr") for name in names)
    valid = {
        "roadrunner-datasmith": has_xodr and any(name.endswith(".udatasmith") for name in names),
        "roadrunner-filmbox": has_xodr
        and any(name.endswith(".fbx") for name in names)
        and any(name.endswith(".rrdata.xml") for name in names),
        "generic-fbx-xodr": has_xodr and any(name.endswith(".fbx") for name in names),
    }[profile]
    return check(
        "RR-EXPORT-CONTRACT",
        "PASS" if valid else "BLOCKED",
        "Required export members were found." if valid else "Required export members are missing.",
        category="input",
        reason_code=None if valid else "RR-EXPORT-MEMBER-MISSING",
    )


def inspect_workspace(workspace: dict[str, Any], route: str) -> dict[str, Any]:
    if route not in ROUTES:
        raise CmtkError("ROUTE-UNKNOWN", "Unknown migration route.", details={"route": route})
    prefix = ROUTES[route]["prefix"]
    checks: list[dict[str, Any]] = []
    version = str(workspace.get("schema_version", ""))
    checks.append(
        check(
            "WORKSPACE-SCHEMA-MAJOR",
            "PASS" if version.startswith("1.") else "BLOCKED",
            "Workspace schema major is supported."
            if version.startswith("1.")
            else "Workspace schema major is unsupported.",
            category="schema",
            reason_code=None if version.startswith("1.") else "SCHEMA-VERSION-UNSUPPORTED",
        )
    )
    declared_route = workspace.get("route")
    checks.append(
        check(
            "WORKSPACE-ROUTE",
            "PASS" if declared_route in (None, route) else "BLOCKED",
            "Workspace route matches the invocation."
            if declared_route in (None, route)
            else "Workspace route conflicts with the invocation.",
            category="route",
            reason_code=None if declared_route in (None, route) else "ROUTE-CONFLICT",
        )
    )
    mode = workspace.get("map", {}).get("mode")
    checks.append(
        check(
            "WORKSPACE-MAP-MODE",
            "PASS" if mode in {"standard", "large-tiled"} else "BLOCKED",
            "Map mode is explicit." if mode in {"standard", "large-tiled"} else "Map mode is missing or unknown.",
            category="profile",
            reason_code=None if mode in {"standard", "large-tiled"} else "MAP-MODE-UNKNOWN",
        )
    )
    checks.extend(_path_checks(workspace))

    source = workspace.get("source_carla", {})
    required_source = all(source.get(field) for field in ("root", "version", "engine_version", "map_asset_path"))
    checks.append(
        check(
            "SOURCE-PROFILE-COMPLETE",
            "PASS" if required_source else "BLOCKED",
            "Source CARLA identity is complete." if required_source else "Source CARLA identity is incomplete.",
            category="environment",
            reason_code=None if required_source else "ENV-CARLA-VERSION-UNKNOWN",
        )
    )
    xodr_path = source.get("xodr_path")
    checks.append(
        check(
            "SOURCE-XODR",
            "PASS" if xodr_path else "BLOCKED",
            "Source OpenDRIVE path is explicit." if xodr_path else "Source OpenDRIVE path is missing.",
            category="input",
            reason_code=None if xodr_path else "SOURCE-XODR-MISSING",
        )
    )

    if route == "roadrunner-to-source-carla":
        checks.append(_rr_export_check(workspace))
    elif route == "source-carla-to-package-carla":
        source_input = workspace.get("input", {})
        input_complete = all(
            source_input.get(field)
            for field in (
                "root",
                "handoff_path",
                "asset_inventory_path",
                "dependency_manifest_path",
                "route_manifest_path",
            )
        )
        checks.append(
            check(
                "SOURCE-INPUT-MANIFESTS",
                "PASS" if input_complete else "BLOCKED",
                "Source CARLA handoff and inventory manifests are explicit."
                if input_complete
                else "Source CARLA handoff or inventory manifests are incomplete.",
                category="input",
                reason_code=None if input_complete else "SOURCE-INPUT-MANIFEST-INCOMPLETE",
            )
        )
        input_profile = source_input.get("profile")
        checks.append(
            check(
                "SOURCE-INPUT-PROFILE",
                "PASS" if input_profile in ROUTES[route]["source_profiles"] else "BLOCKED",
                "Source CARLA input profile is supported."
                if input_profile in ROUTES[route]["source_profiles"]
                else "Source CARLA input profile is unknown.",
                category="profile",
                reason_code=None
                if input_profile in ROUTES[route]["source_profiles"]
                else "SOURCE-INPUT-PROFILE-UNKNOWN",
            )
        )
        package = workspace.get("package_carla", {})
        source_platform = source.get("platform")
        target_platform = package.get("platform")
        matches = bool(source_platform and target_platform and source_platform == target_platform)
        checks.append(
            check(
                "PKG-TARGET-PLATFORM",
                "PASS" if matches else "BLOCKED",
                "Build and target platforms match." if matches else "Build and target platforms differ or are unknown.",
                category="platform",
                reason_code=None if matches else "PKG-TARGET-PLATFORM-MISMATCH",
            )
        )
        source_version = source.get("version")
        package_version = package.get("version")
        version_matches = bool(source_version and package_version and source_version == package_version)
        checks.append(
            check(
                "PKG-TARGET-VERSION",
                "PASS" if version_matches else "BLOCKED",
                "Source and Package CARLA versions match."
                if version_matches
                else "Source and Package CARLA versions differ or are unknown.",
                category="version",
                reason_code=None if version_matches else "PKG-TARGET-VERSION-MISMATCH",
            )
        )
        profile = package.get("profile")
        allowed = ROUTES[route]["target_profiles"]
        checks.append(
            check(
                "PKG-OUTPUT-PROFILE",
                "PASS" if profile in allowed else "BLOCKED",
                "Package output profile is supported." if profile in allowed else "Package output profile is unknown.",
                category="profile",
                reason_code=None if profile in allowed else "PKG-OUTPUT-PROFILE-UNKNOWN",
            )
        )
    else:
        source_input = workspace.get("input", {})
        input_complete = all(
            source_input.get(field)
            for field in (
                "root",
                "handoff_path",
                "asset_inventory_path",
                "dependency_manifest_path",
                "route_manifest_path",
            )
        )
        checks.append(
            check(
                "SOURCE-INPUT-MANIFESTS",
                "PASS" if input_complete else "BLOCKED",
                "Source CARLA handoff and inventory manifests are explicit."
                if input_complete
                else "Source CARLA handoff or inventory manifests are incomplete.",
                category="input",
                reason_code=None if input_complete else "SOURCE-INPUT-MANIFEST-INCOMPLETE",
            )
        )
        input_profile = source_input.get("profile")
        checks.append(
            check(
                "SOURCE-INPUT-PROFILE",
                "PASS" if input_profile in ROUTES[route]["source_profiles"] else "BLOCKED",
                "Source CARLA input profile is supported."
                if input_profile in ROUTES[route]["source_profiles"]
                else "Source CARLA input profile is unknown.",
                category="profile",
                reason_code=None
                if input_profile in ROUTES[route]["source_profiles"]
                else "SOURCE-INPUT-PROFILE-UNKNOWN",
            )
        )
        ue = workspace.get("ue427", {})
        profile = ue.get("profile")
        complete = all(
            ue.get(field)
            for field in ("engine_root", "engine_version", "uproject", "map_asset_path", "cold_copy_uproject")
        )
        checks.append(
            check(
                "UE427-TARGET-PROJECT",
                "PASS" if complete else "BLOCKED",
                "UE4.27 target and cold-copy projects are explicit."
                if complete
                else "UE4.27 target or cold-copy project is incomplete.",
                category="environment",
                reason_code=None if complete else "UE427-TARGET-PROJECT-INVALID",
            )
        )
        checks.append(
            check(
                "UE427-TARGET-PROFILE",
                "PASS" if profile in ROUTES[route]["target_profiles"] else "BLOCKED",
                "UE4.27 target profile is supported."
                if profile in ROUTES[route]["target_profiles"]
                else "UE4.27 target profile is unknown.",
                category="profile",
                reason_code=None if profile in ROUTES[route]["target_profiles"] else "UE427-TARGET-PROFILE-UNKNOWN",
            )
        )
        engine_version = str(ue.get("engine_version", ""))
        engine_matches = engine_version == "4.27" or engine_version.startswith("4.27.")
        checks.append(
            check(
                "UE427-ENGINE-VERSION",
                "PASS" if engine_matches else "BLOCKED",
                "Target engine is Unreal Engine 4.27."
                if engine_matches
                else "Target engine is not an identified Unreal Engine 4.27 build.",
                category="version",
                reason_code=None if engine_matches else "UE427-ENGINE-VERSION-MISMATCH",
            )
        )
        checks.append(_ue427_dependency_check(workspace))

    has_blocker = any(item["status"] in {"FAIL", "BLOCKED"} for item in checks)
    return stage_result(
        route=route,
        stage=f"{prefix}.DISCOVER_INPUT" if route == "roadrunner-to-source-carla" else f"{prefix}.PREFLIGHT",
        checks=checks,
        actions=["resolved workspace paths", "validated route and profiles"],
        next_allowed_stages=[]
        if has_blocker
        else [f"{prefix}.PREFLIGHT_ENV" if route == "roadrunner-to-source-carla" else f"{prefix}.BASELINE"],
    )
