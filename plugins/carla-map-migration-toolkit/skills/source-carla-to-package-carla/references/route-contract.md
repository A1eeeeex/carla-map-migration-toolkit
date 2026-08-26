# Source CARLA to Package CARLA route contract

Profiles: `content-package` and `full-carla-package`. Build and target Package
CARLA OS/architecture must match exactly.

Required stages:

```text
SRC2PKG.READ_HANDOFF
SRC2PKG.PREFLIGHT
SRC2PKG.BASELINE
SRC2PKG.SELECT_OUTPUT
SRC2PKG.AUDIT_CONFIG
SRC2PKG.AUDIT_COOK_DEPS
SRC2PKG.REPAIR
SRC2PKG.BUILD
SRC2PKG.ARCHIVE_AUDIT
SRC2PKG.BACKUP_TARGET
SRC2PKG.IMPORT
SRC2PKG.RUNTIME_VALIDATE
SRC2PKG.OPTIMIZE
SRC2PKG.HANDOFF
```

Source CARLA is the repair/build source; Package CARLA is only the import and
validation target. Audit external archives before extraction. `load_world()`
alone is insufficient: also evaluate registration, visuals, collision, XODR,
spawn, relevant traffic/navigation, dynamic smoke, and stability.
