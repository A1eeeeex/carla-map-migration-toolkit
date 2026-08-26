from __future__ import annotations

from typing import Any

REQUIRED_CHECKS = {
    "roadrunner-to-source-carla": [
        "Editor reopen and saved assets",
        "asset-reference audit",
        "fixed-camera material review",
        "XODR and topology",
        "spawn points and route sample",
        "road collision smoke test",
        "Traffic Manager and traffic-light probes when applicable",
        "pedestrian navigation when declared",
        "fixed-duration server stability",
    ],
    "source-carla-to-package-carla": [
        "archive safety and required members",
        "target backup and import",
        "map registry and world load",
        "fixed-camera material review",
        "XODR, topology, and spawn points",
        "road collision and dynamic smoke test",
        "Traffic Manager and navigation when applicable",
        "fixed-duration runtime stability",
    ],
    "source-carla-to-ue427": [
        "dependency allowlist",
        "material compile and fixed-camera review",
        "World Settings and replacement policy",
        "road collision",
        "target project reopen and PIE",
        "cold-copy dependency allowlist",
        "cold-copy reopen and PIE",
    ],
}


def pending_validation_report(workspace: dict[str, Any], route: str) -> dict[str, Any]:
    if route == "roadrunner-to-source-carla":
        target_profile = "source-carla-map"
    elif route == "source-carla-to-package-carla":
        target_profile = workspace.get("package_carla", {}).get("profile", "unknown")
    else:
        target_profile = workspace.get("ue427", {}).get("profile", "unknown")
    source = workspace.get("source_carla", {})
    return {
        "schema_version": "1.0.0",
        "route": route,
        "target_profile": target_profile,
        "overall_status": "NOT_RUN",
        "required_checks": [],
        "optional_checks": [],
        "not_run_checks": REQUIRED_CHECKS[route],
        "blockers": [],
        "evidence_level": "L1_LOGIC",
        "environment": {
            "source_carla_version": source.get("version"),
            "source_engine_version": source.get("engine_version"),
        },
        "artifacts": [],
        "remaining_risk": [
            "No Editor, CARLA runtime, build, import, PIE, or cold-copy evidence was supplied to this host-only report."
        ],
    }
