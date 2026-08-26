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
