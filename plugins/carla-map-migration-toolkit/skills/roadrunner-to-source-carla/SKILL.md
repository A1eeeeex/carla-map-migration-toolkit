---
name: roadrunner-to-source-carla
description: Migrate a custom map from a RoadRunner Datasmith, legacy Filmbox, or generic FBX/XODR export into a CARLA source build. Use for import preflight, Dataprep checkpoints, post-import material/reference/alignment/collision/traffic repairs, route-scoped performance profiling and optimization after functional validation, Source CARLA validation, and downstream handoff. Do not use when the target is Package CARLA or vanilla UE4.27, or for unrelated engine tuning.
---

# RoadRunner to Source CARLA

## Invocation Contract

Accept a normal migration request. Do not require internal command, profile, or
artifact names. Before writing, identify the RoadRunner export profile, map mode,
map name, Source CARLA and engine identities, target asset path, allowed roots,
artifact root, backup root, and authorized execution mode. If any required fact
is unknown, remain read-only and report it.

## Use This Skill When

- The source is `.udatasmith` plus XODR, or legacy FBX/rrdata plus XODR.
- A RoadRunner import into editable Source CARLA needs inspection or repair.
- Dataprep commit/save, material, alignment, collision, traffic, or navigation
  evidence is missing after import.

## Do Not Use This Skill When

- A Source CARLA map must be packaged for binary CARLA.
- A Source CARLA map must be detached into vanilla UE4.27.
- The request is only XODR conformance, RoadRunner authoring, or HDMap conversion.

## Workflow

1. Load `references/route-contract.md` and only the relevant shared references.
2. Classify `roadrunner-datasmith`, `roadrunner-filmbox`, or
   `generic-fbx-xodr`; keep `standard` and `large-tiled` separate.
3. Run inspect, capture hashes/baseline, then generate a plan.
4. Treat Dataprep Import, Execute, Commit, and Save as `EDITOR_CHECKPOINT` steps.
5. Audit actual assets after every checkpoint; never accept a verbal completion
   as evidence.
6. Apply only reviewed repairs through the correct execution context and Unreal
   APIs. Never move Unreal assets with host filesystem operations.
7. Validate Editor reopen, saved assets, references, materials, XODR/topology,
   spawn/route, collision, traffic, navigation where declared, and stability.
8. Optimize only after functional baseline; emit a Source handoff only from
   referenced stage artifacts.

## Load on demand

- For import/save failures, alignment, missing assets or resource pressure, read
  [Source and package operations](../../references/carla-map-operations.md).
- For a slow imported map, read
  [map performance operations](../../references/map-performance-operations.md).
  Reuse comparable existing samples; do not restart the import to compare them.

## Shared Commands

Run these from the repository clone root after completing `docs/installation.md`.
If that root or its `.venv` cannot be resolved, remain read-only and report the
installation blocker instead of guessing another interpreter or script path.

```bash
CMTK_EXECUTION_CONTEXT=host-cpython .venv/bin/python plugins/carla-map-migration-toolkit/scripts/cmtk.py inspect --route roadrunner-to-source-carla --config <map-workspace.json>
CMTK_EXECUTION_CONTEXT=host-cpython .venv/bin/python plugins/carla-map-migration-toolkit/scripts/cmtk.py plan --route roadrunner-to-source-carla --config <map-workspace.json> --output <artifact-root>/route-plan.json
CMTK_EXECUTION_CONTEXT=host-cpython .venv/bin/python plugins/carla-map-migration-toolkit/scripts/cmtk.py validate --route roadrunner-to-source-carla --config <map-workspace.json> --output <artifact-root>/validation-report.json
```

The host core is read-only except for writing artifacts under `artifact_root`.
It reports environment checks as `NOT_RUN` until the matching Editor/runtime
adapter supplies evidence.

## Final Response

Report route/Profile, environment/version facts, detected issues, plan or actual
changes, validation level/results, evidence artifacts, NOT_RUN items, remaining
risk, backup, and rollback. Never render `NOT_RUN` as success.
