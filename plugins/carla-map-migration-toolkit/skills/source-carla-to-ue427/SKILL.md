---
name: source-carla-to-ue427
description: Detach and migrate a custom map from a CARLA source project into clean vanilla Unreal Engine 4.27. Use for Unreal-API asset migration, CARLA/plugin dependency classification, material/reference/world/collision repair, CARLA-class replacement, optional optimization, and mandatory second-project cold-copy validation. Do not use for CARLA packaging or UE5-to-UE4 downgrade.
---

# Source CARLA to Unreal Engine 4.27

## Invocation Contract

Accept a Source handoff or inspect the Source project. Before writing, prove the
Source map/engine identity, clean vanilla UE4.27 engine/project, target profile,
target asset path, replacement policy, second cold-copy project, allowed roots,
artifact root, backup root, and authorized execution mode. Do not promise CARLA
server, sensor, Traffic Manager, or Python API behavior in vanilla UE4.27.

## Use This Skill When

- A Source CARLA map must become a `standalone-map` in vanilla UE4.27.
- CARLA/plugin references, black materials, missing classes, invalid World
  Settings, or collision failures remain after migration.
- Acceptance requires a second clean-project cold-copy.
- The optional `hil-ready` profile is explicitly requested and evaluated apart.

## Do Not Use This Skill When

- The target is Package CARLA.
- The source is still a RoadRunner export.
- The task is a UE5/CARLA 0.10 downgrade or expects automatic CARLA services.

## Workflow

1. Load `references/route-contract.md` and only relevant shared references.
2. Revalidate Source evidence and capture dependency, reference, material,
   transform, collision, world, and performance baselines.
3. Classify dependencies as portable, localizable, replaceable, removable,
   editor-only, or blocked; define every replacement before applying it.
4. Generate and review a plan.
5. Migrate assets only through AssetTools, Migrate, EditorAssetLibrary, Asset
   Registry, or equivalent engine APIs. Never use raw OS move/rename/delete.
6. Localize approved dependencies; replace/remove CARLA-specific classes; repair
   environment, World Settings, collision, redirectors, and allowlist violations.
7. Reopen and run PIE/visual/collision checks in the primary target.
8. Copy only delivery content into a second clean project through an approved
   Unreal workflow and repeat dependency, reopen, PIE, visual, and collision gates.
9. Keep `standalone-map` and `hil-ready` results separate. Without cold-copy,
   overall acceptance is not `PASS`.

## Shared Commands

```bash
python3 ../../scripts/cmtk.py inspect --route source-carla-to-ue427 --config <map-workspace.json>
python3 ../../scripts/cmtk.py plan --route source-carla-to-ue427 --config <map-workspace.json> --output <artifact-root>/route-plan.json
python3 ../../scripts/cmtk.py validate --route source-carla-to-ue427 --config <map-workspace.json> --output <artifact-root>/validation-report.json
```

The host core writes only reviewed artifacts. Unreal migration, PIE, and
cold-copy checks stay `NOT_RUN` until their declared contexts supply evidence.

## Final Response

Report profiles/versions, dependency classification, changes and replacements,
material/reference/world/collision findings, target and cold-copy checks, HIL
result separately, evidence, NOT_RUN items, risk, backup, and rollback.
