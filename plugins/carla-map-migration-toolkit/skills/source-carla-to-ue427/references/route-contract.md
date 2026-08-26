# Source CARLA to UE4.27 route contract

Profiles: `standalone-map` and experimental `hil-ready`. The target is vanilla
UE4.27, not a CARLA service runtime.

Required stages:

```text
SRC2UE427.READ_HANDOFF
SRC2UE427.PREFLIGHT
SRC2UE427.BASELINE
SRC2UE427.CLASSIFY_DEPS
SRC2UE427.CREATE_TARGET
SRC2UE427.MIGRATE_ASSETS
SRC2UE427.REPAIR_MATERIALS
SRC2UE427.REPLACE_CARLA
SRC2UE427.REPAIR_WORLD
SRC2UE427.REPAIR_COLLISION
SRC2UE427.CLEAN_REFS
SRC2UE427.TARGET_VALIDATE
SRC2UE427.OPTIMIZE
SRC2UE427.COLD_COPY
SRC2UE427.HIL_VALIDATE
SRC2UE427.HANDOFF
```

Classify dependencies as portable, localizable, replaceable, removable,
editor-only, or blocked. Unknown replacements block. Migration uses Unreal APIs,
never OS moves. The primary project is not acceptance; the second clean project
must pass allowlist, reopen, PIE, material/visual, and collision checks.
