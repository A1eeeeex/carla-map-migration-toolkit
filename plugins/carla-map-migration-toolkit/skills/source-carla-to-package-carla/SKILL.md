---
name: source-carla-to-package-carla
description: Migrate a validated custom map from a CARLA source build into a matching Package CARLA deployment. Use for content-package or full-carla-package planning, Package JSON and MapsToCook repair, Cook dependency and archive audit, target backup/import, independent runtime validation, and rollback. Do not use for first RoadRunner import or vanilla UE4.27 detachment.
---

# Source CARLA to Package CARLA

## Invocation Contract

Accept a Source handoff or inspect the live Source project. Before writing, prove
the Source map identity, `content-package` or `full-carla-package` target, Source
build OS/architecture, matching Package CARLA version/OS/architecture, Cook
contract, artifact root, backup root, and replacement authorization.

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

## Shared Commands

```bash
python3 ../../scripts/cmtk.py inspect --route source-carla-to-package-carla --config <map-workspace.json>
python3 ../../scripts/cmtk.py plan --route source-carla-to-package-carla --config <map-workspace.json> --output <artifact-root>/route-plan.json
python3 ../../scripts/cmtk.py archive-audit --archive <package.tar.gz> --allowed-root <archive-root> --require '*.umap' --require '*.xodr'
python3 ../../scripts/cmtk.py validate --route source-carla-to-package-carla --config <map-workspace.json> --output <artifact-root>/validation-report.json
```

The host core never extracts the archive. Build, import, and CARLA runtime checks
remain `NOT_RUN` until their declared contexts produce evidence.

## Final Response

Report versions/platforms, output profile, Cook findings, build and archive
evidence, target backup/import, independent validation, handoff, NOT_RUN items,
remaining risk, and rollback.
