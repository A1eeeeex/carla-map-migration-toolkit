# RoadRunner to Source CARLA route contract

Profiles: `roadrunner-datasmith`, experimental `roadrunner-filmbox`, and limited
`generic-fbx-xodr`; map modes are `standard` and `large-tiled`.

Required stages:

```text
RR2SRC.DISCOVER_INPUT
RR2SRC.PREFLIGHT_ENV
RR2SRC.VALIDATE_EXPORT
RR2SRC.BASELINE
RR2SRC.PREPARE_TARGET
RR2SRC.IMPORT
RR2SRC.POST_IMPORT_AUDIT
RR2SRC.REPAIR
RR2SRC.FUNCTIONAL_VALIDATE
RR2SRC.OPTIMIZE
RR2SRC.TARGET_VALIDATE
RR2SRC.HANDOFF
```

Datasmith Import/Execute/Commit/Save are checkpoints. Filmbox commands must be
resolved from the current CARLA checkout and `--help`. The minimum handoff gate
covers Editor reopen/save, references, fixed-camera materials, XODR/topology,
spawn/route, collision, declared traffic/navigation capability, and stability.
