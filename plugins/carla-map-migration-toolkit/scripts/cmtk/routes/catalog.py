from __future__ import annotations

ROUTES = {
    "roadrunner-to-source-carla": {
        "prefix": "RR2SRC",
        "source_profiles": {"roadrunner-datasmith", "roadrunner-filmbox", "generic-fbx-xodr"},
        "target_profiles": {"source-carla-map"},
    },
    "source-carla-to-package-carla": {
        "prefix": "SRC2PKG",
        "source_profiles": {"source-carla-map"},
        "target_profiles": {"content-package", "full-carla-package"},
    },
    "source-carla-to-ue427": {
        "prefix": "SRC2UE427",
        "source_profiles": {"source-carla-map"},
        "target_profiles": {"standalone-map", "hil-ready"},
    },
}


STEP_CATALOG = {
    "roadrunner-to-source-carla": [
        ("DISCOVER_INPUT", "AUTO", "host-cpython", "low"),
        ("PREFLIGHT_ENV", "AUTO", "host-cpython", "low"),
        ("VALIDATE_EXPORT", "AUTO", "host-cpython", "low"),
        ("BASELINE", "AUTO", "source-unreal-python", "low"),
        ("PREPARE_TARGET", "REVIEW_REQUIRED", "source-unreal-python", "medium"),
        ("IMPORT", "EDITOR_CHECKPOINT", "source-unreal-python", "high"),
        ("POST_IMPORT_AUDIT", "AUTO", "source-unreal-python", "low"),
        ("REPAIR", "REVIEW_REQUIRED", "source-unreal-python", "high"),
        ("FUNCTIONAL_VALIDATE", "AUTO", "carla-client-python", "low"),
        ("OPTIMIZE", "REVIEW_REQUIRED", "source-unreal-python", "high"),
        ("TARGET_VALIDATE", "AUTO", "carla-client-python", "low"),
        ("HANDOFF", "AUTO", "host-cpython", "low"),
    ],
    "source-carla-to-package-carla": [
        ("READ_HANDOFF", "AUTO", "host-cpython", "low"),
        ("SELECT_OUTPUT", "AUTO", "host-cpython", "low"),
        ("PREFLIGHT", "AUTO", "host-cpython", "low"),
        ("BASELINE", "AUTO", "host-cpython", "low"),
        ("AUDIT_CONFIG", "AUTO", "host-cpython", "low"),
        ("AUDIT_COOK_DEPS", "EDITOR_CHECKPOINT", "source-unreal-python", "medium"),
        ("REPAIR", "REVIEW_REQUIRED", "source-unreal-python", "high"),
        ("BUILD", "REVIEW_REQUIRED", "shell-build", "high"),
        ("ARCHIVE_AUDIT", "AUTO", "host-cpython", "low"),
        ("BACKUP_TARGET", "REVIEW_REQUIRED", "shell-build", "high"),
        ("IMPORT", "REVIEW_REQUIRED", "shell-build", "high"),
        ("RUNTIME_VALIDATE", "AUTO", "carla-client-python", "low"),
        ("OPTIMIZE", "REVIEW_REQUIRED", "source-unreal-python", "high"),
        ("HANDOFF", "AUTO", "host-cpython", "low"),
    ],
    "source-carla-to-ue427": [
        ("READ_HANDOFF", "AUTO", "host-cpython", "low"),
        ("PREFLIGHT", "AUTO", "host-cpython", "low"),
        ("BASELINE", "AUTO", "source-unreal-python", "low"),
        ("CLASSIFY_DEPS", "REVIEW_REQUIRED", "host-cpython", "medium"),
        ("CREATE_TARGET", "EDITOR_CHECKPOINT", "ue427-unreal-python", "medium"),
        ("MIGRATE_ASSETS", "REVIEW_REQUIRED", "source-unreal-python", "high"),
        ("REPAIR_MATERIALS", "REVIEW_REQUIRED", "ue427-unreal-python", "high"),
        ("REPLACE_CARLA", "REVIEW_REQUIRED", "ue427-unreal-python", "high"),
        ("REPAIR_WORLD", "REVIEW_REQUIRED", "ue427-unreal-python", "high"),
        ("REPAIR_COLLISION", "REVIEW_REQUIRED", "ue427-unreal-python", "high"),
        ("CLEAN_REFS", "REVIEW_REQUIRED", "ue427-unreal-python", "high"),
        ("TARGET_VALIDATE", "AUTO", "ue427-unreal-python", "low"),
        ("OPTIMIZE", "REVIEW_REQUIRED", "ue427-unreal-python", "high"),
        ("COLD_COPY", "EDITOR_CHECKPOINT", "ue427-unreal-python", "high"),
        ("HIL_VALIDATE", "AUTO", "ue427-unreal-python", "low"),
        ("HANDOFF", "AUTO", "host-cpython", "low"),
    ],
}


REQUIRED_CHECK_STAGES = {
    "roadrunner-to-source-carla": {
        "input_profile_identified": ("RR2SRC.DISCOVER_INPUT",),
        "environment_versions_recorded": ("RR2SRC.PREFLIGHT_ENV",),
        "source_target_identified": ("RR2SRC.PREFLIGHT_ENV",),
        "import_committed_saved": ("RR2SRC.IMPORT",),
        "editor_reopen": ("RR2SRC.POST_IMPORT_AUDIT",),
        "opendrive_map_match": ("RR2SRC.FUNCTIONAL_VALIDATE",),
        "spawn_points_profile": ("RR2SRC.FUNCTIONAL_VALIDATE",),
        "topology_junction_core": ("RR2SRC.FUNCTIONAL_VALIDATE",),
        "vehicle_spawn_collision": ("RR2SRC.FUNCTIONAL_VALIDATE",),
        "required_materials_valid": ("RR2SRC.POST_IMPORT_AUDIT",),
        "external_refs_resolved": ("RR2SRC.POST_IMPORT_AUDIT",),
        "source_handoff_complete": ("RR2SRC.HANDOFF",),
    },
    "source-carla-to-package-carla": {
        "source_handoff_passed": ("SRC2PKG.READ_HANDOFF",),
        "build_target_os_match": ("SRC2PKG.PREFLIGHT",),
        "package_config_valid": ("SRC2PKG.AUDIT_CONFIG",),
        "cook_dependencies_complete": ("SRC2PKG.AUDIT_COOK_DEPS",),
        "package_artifact_hashed": ("SRC2PKG.BUILD",),
        "archive_safety_passed": ("SRC2PKG.ARCHIVE_AUDIT",),
        "target_backup_complete": ("SRC2PKG.BACKUP_TARGET",),
        "package_registry_visible": ("SRC2PKG.RUNTIME_VALIDATE",),
        "load_world_stable": ("SRC2PKG.RUNTIME_VALIDATE",),
        "source_visual_parity": ("SRC2PKG.RUNTIME_VALIDATE",),
        "road_collision_smoke": ("SRC2PKG.RUNTIME_VALIDATE",),
        "opendrive_spawn_expected": ("SRC2PKG.RUNTIME_VALIDATE",),
        "dynamic_smoke": ("SRC2PKG.RUNTIME_VALIDATE",),
        "rollback_ready": ("SRC2PKG.HANDOFF",),
    },
    "source-carla-to-ue427": {
        "source_asset_inventory_complete": ("SRC2UE427.BASELINE",),
        "dependency_classification_complete": ("SRC2UE427.CLASSIFY_DEPS",),
        "unreal_safe_migration": ("SRC2UE427.MIGRATE_ASSETS",),
        "target_engine_version_recorded": ("SRC2UE427.CREATE_TARGET",),
        "required_assets_present": ("SRC2UE427.TARGET_VALIDATE",),
        "missing_assets_zero": ("SRC2UE427.TARGET_VALIDATE",),
        "required_materials_valid": ("SRC2UE427.TARGET_VALIDATE",),
        "disallowed_carla_refs_zero": ("SRC2UE427.CLEAN_REFS",),
        "runtime_objects_have_strategy": ("SRC2UE427.REPLACE_CARLA",),
        "world_settings_environment_lighting": ("SRC2UE427.REPAIR_WORLD",),
        "road_collision_smoke": ("SRC2UE427.TARGET_VALIDATE",),
        "target_reopen": ("SRC2UE427.TARGET_VALIDATE",),
        "pie_smoke": ("SRC2UE427.TARGET_VALIDATE",),
        "second_clean_project_cold_copy": ("SRC2UE427.COLD_COPY",),
        "ue427_handoff_complete": ("SRC2UE427.HANDOFF",),
    },
}


REQUIRED_CHECK_EVIDENCE_TYPES = {
    "roadrunner-to-source-carla": {
        "input_profile_identified": "deterministic-output",
        "environment_versions_recorded": "deterministic-output",
        "source_target_identified": "deterministic-output",
        "import_committed_saved": "editor-audit",
        "editor_reopen": "editor-audit",
        "opendrive_map_match": "runtime-measurement",
        "spawn_points_profile": "runtime-measurement",
        "topology_junction_core": "runtime-measurement",
        "vehicle_spawn_collision": "runtime-measurement",
        "required_materials_valid": "editor-audit",
        "external_refs_resolved": "editor-audit",
        "source_handoff_complete": "deterministic-output",
    },
    "source-carla-to-package-carla": {
        "source_handoff_passed": "deterministic-output",
        "build_target_os_match": "deterministic-output",
        "package_config_valid": "deterministic-output",
        "cook_dependencies_complete": "deterministic-output",
        "package_artifact_hashed": "deterministic-output",
        "archive_safety_passed": "deterministic-output",
        "target_backup_complete": "deterministic-output",
        "package_registry_visible": "runtime-measurement",
        "load_world_stable": "runtime-measurement",
        "source_visual_parity": "runtime-measurement",
        "road_collision_smoke": "runtime-measurement",
        "opendrive_spawn_expected": "runtime-measurement",
        "dynamic_smoke": "runtime-measurement",
        "rollback_ready": "deterministic-output",
    },
    "source-carla-to-ue427": {
        "source_asset_inventory_complete": "deterministic-output",
        "dependency_classification_complete": "deterministic-output",
        "unreal_safe_migration": "editor-audit",
        "target_engine_version_recorded": "editor-audit",
        "required_assets_present": "editor-audit",
        "missing_assets_zero": "editor-audit",
        "required_materials_valid": "editor-audit",
        "disallowed_carla_refs_zero": "editor-audit",
        "runtime_objects_have_strategy": "editor-audit",
        "world_settings_environment_lighting": "editor-audit",
        "road_collision_smoke": "runtime-measurement",
        "target_reopen": "editor-audit",
        "pie_smoke": "runtime-measurement",
        "second_clean_project_cold_copy": "portability-replay",
        "ue427_handoff_complete": "deterministic-output",
    },
}


OPTIONAL_STAGE_CHECK_STAGES = {
    "roadrunner-to-source-carla": {
        "repair_contract_complete": ("RR2SRC.REPAIR",),
        "optimization_apply_verified": ("RR2SRC.OPTIMIZE",),
    },
    "source-carla-to-package-carla": {
        "repair_contract_complete": ("SRC2PKG.REPAIR",),
        "optimization_apply_verified": ("SRC2PKG.OPTIMIZE",),
    },
    "source-carla-to-ue427": {
        "repair_contract_complete": (
            "SRC2UE427.REPAIR_MATERIALS",
            "SRC2UE427.REPLACE_CARLA",
            "SRC2UE427.REPAIR_WORLD",
            "SRC2UE427.REPAIR_COLLISION",
            "SRC2UE427.CLEAN_REFS",
        ),
        "optimization_apply_verified": ("SRC2UE427.OPTIMIZE",),
    },
}


OPTIONAL_STAGE_CHECK_EVIDENCE_TYPES = {
    route: {
        "repair_contract_complete": "editor-audit",
        "optimization_apply_verified": "editor-audit",
    }
    for route in ROUTES
}
