---
name: source-carla-to-package-carla
description: Migrate a validated custom map from a CARLA source build into a matching Package CARLA deployment. Use for content-package or full-carla-package planning, Package JSON and MapsToCook repair, cooked map/XODR/sidecar and archive audit, target backup/import, route-scoped performance profiling and optimization, independent runtime validation, and rollback. Do not use for first RoadRunner import, vanilla UE4.27 detachment, or unrelated engine tuning.
---

# Source CARLA to Package CARLA

## Invocation Contract

Accept a Source handoff or inspect the live Source project. Before writing, prove
the Source map identity, `content-package` or `full-carla-package` target, Source
build OS/architecture, matching Package CARLA version/OS/architecture, Cook
contract, artifact root, backup root, and replacement authorization.

For an archive-only audit, inspect the supplied archive and known map name
without requiring a live server. Do not promote that result to route acceptance.

## Use This Skill When

- A map works in Source CARLA and must run in a binary CARLA deployment.
- Cook omits a map, material, texture, XODR, or soft dependency.
- Archive import, map registration, world load, collision, or runtime validation
  fails in Package CARLA.

## Do Not Use This Skill When

- The source is a RoadRunner export not yet imported into Source CARLA.
- The target is vanilla UE4.27.
- The proposed solution is copying one `.umap` into a binary installation.

## Workflow

1. Load `references/route-contract.md` and relevant shared references.
2. Revalidate the Source handoff and select an output profile.
3. Hard-block build/target platform mismatch or unknown critical versions.
4. Baseline Source and target; audit Package JSON, MapsToCook, naming,
   redirectors, soft references, saved state, and Cook reachability.
5. Generate a plan before configuration or dependency repairs.
6. Resolve build/import commands from the checked-out version; do not rely on
   remembered command lines.
7. Inspect archive paths, links, duplicates, declared expansion size, map, and
   XODR before extraction.
8. Create a timestamped target backup before replacing a same-name map.
9. Independently validate registration, load, visuals, collision, XODR, spawn,
   traffic/navigation where applicable, dynamic smoke, and stability.
10. Roll back on failure; emit a Package handoff only from referenced evidence.

## Load on demand

- For Cook omissions, empty worlds, sidecars, import failures or VRAM pressure,
  read [Source and package operations](../../references/carla-map-operations.md).
- For package-route profiling or optimization, read
  [map performance operations](../../references/map-performance-operations.md).

## Shared Commands

Run these from the repository clone root after completing `docs/installation.md`.
If that root or its `.venv` cannot be resolved, remain read-only and report the
installation blocker instead of guessing another interpreter or script path.

```bash
CMTK_EXECUTION_CONTEXT=host-cpython .venv/bin/python plugins/carla-map-migration-toolkit/scripts/cmtk.py inspect --route source-carla-to-package-carla --config <map-workspace.json>
CMTK_EXECUTION_CONTEXT=host-cpython .venv/bin/python plugins/carla-map-migration-toolkit/scripts/cmtk.py plan --route source-carla-to-package-carla --config <map-workspace.json> --output <artifact-root>/route-plan.json
CMTK_EXECUTION_CONTEXT=host-cpython .venv/bin/python plugins/carla-map-migration-toolkit/scripts/cmtk.py archive-audit --archive <package.tar.gz> --allowed-root <archive-root> --require '*.umap' --require '*.xodr'
CMTK_EXECUTION_CONTEXT=host-cpython .venv/bin/python plugins/carla-map-migration-toolkit/scripts/cmtk.py map-package-audit --target <package.tar.gz> --allowed-root <archive-root> --map-name ExampleMap
CMTK_EXECUTION_CONTEXT=host-cpython .venv/bin/python plugins/carla-map-migration-toolkit/scripts/cmtk.py validate --route source-carla-to-package-carla --config <map-workspace.json> --output <artifact-root>/validation-report.json
```

The host core never extracts the archive. Build, import, and CARLA runtime checks
remain `NOT_RUN` until their declared contexts produce evidence.

## Final Response

Report versions/platforms, output profile, Cook findings, build and archive
evidence, target backup/import, independent validation, handoff, NOT_RUN items,
remaining risk, and rollback.
