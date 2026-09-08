---
name: source-carla-to-ue427
description: Detach and migrate a custom map from CARLA into clean vanilla Unreal Engine 4.27, or resume Content-only delivery of an already migrated CARLA-origin UE4.27 map. Use for dependency and class replacement, black-material/daylight/reference/collision repair, Content archive/layout/SHA256 audits and manifests, route-scoped performance profiling and optimization, and second-project cold-copy validation. Do not use for CARLA packaging, unrelated Unreal projects, or UE5-to-UE4 downgrade.
---

# Source CARLA to Unreal Engine 4.27

## Invocation Contract

Accept a Source handoff or inspect the Source project. Before writing, prove the
Source map/engine identity, clean vanilla UE4.27 engine/project, target profile,
target asset path, replacement policy, second cold-copy project, allowed roots,
artifact root, backup root, and authorized execution mode. Do not promise CARLA
server, sensor, Traffic Manager, or Python API behavior in vanilla UE4.27.

If a CARLA-origin map is already native UE4.27, resume at Content delivery;
read the delivery guide below and existing evidence instead of requiring a
new Source import. Read-only archive/manifest checks need only their explicit
inputs and allowed roots. Missing historical evidence blocks full route claims,
not those inspections. Asset writes still require the reviewed route plan.

## Use This Skill When

- A Source CARLA map must become a `standalone-map` in vanilla UE4.27.
- CARLA/plugin references, black materials, missing classes, invalid World
  Settings, or collision failures remain after migration.
- Acceptance requires a second clean-project cold-copy.
- An already migrated map needs a fixed-format Content-only delivery, manifest,
  archive inspection, receiver troubleshooting or performance comparison.
- The optional `hil-ready` profile is explicitly requested and evaluated apart.

## Do Not Use This Skill When

- The target is Package CARLA.
- The source is still a RoadRunner export.
- The task is a UE5/CARLA 0.10 downgrade or expects automatic CARLA services.

## Workflow

1. Load `references/route-contract.md` and only relevant shared references.
2. Revalidate Source evidence and capture dependency, reference, material,
   transform, collision, world, and performance baselines.
3. Classify dependencies as `portable`, `localizable`, `replaceable`, `remove`,
   `blocked`, or `unknown`; unknown and blocked entries stop execution, and
   every replacement must be defined before applying it.
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

## Load on demand

- For Content-only export/copy, fixed mount paths, black materials, daylight
  or receiver acceptance, read
  [UE4.27 Content delivery](../../references/ue427-content-delivery.md).
- For moving-route profiling, optimization candidates or existing metric data,
  read [map performance operations](../../references/map-performance-operations.md).
  Select the checks affected by a change; do not rerun the whole migration for
  a structure audit or numeric comparison.

## Shared Commands

Run these from the repository clone root after completing `docs/installation.md`.
If that root or its `.venv` cannot be resolved, remain read-only and report the
installation blocker instead of guessing another interpreter or script path.

```bash
CMTK_EXECUTION_CONTEXT=host-cpython .venv/bin/python plugins/carla-map-migration-toolkit/scripts/cmtk.py inspect --route source-carla-to-ue427 --config <map-workspace.json>
CMTK_EXECUTION_CONTEXT=host-cpython .venv/bin/python plugins/carla-map-migration-toolkit/scripts/cmtk.py plan --route source-carla-to-ue427 --config <map-workspace.json> --output <artifact-root>/route-plan.json
CMTK_EXECUTION_CONTEXT=host-cpython .venv/bin/python plugins/carla-map-migration-toolkit/scripts/cmtk.py validate --route source-carla-to-ue427 --config <map-workspace.json> --output <artifact-root>/validation-report.json
CMTK_EXECUTION_CONTEXT=host-cpython .venv/bin/python plugins/carla-map-migration-toolkit/scripts/cmtk.py content-audit --target <delivery.tar.gz> --allowed-root <archive-root> --asset-root MAPS/Example --map-name ExampleMap
```

The host core writes only reviewed artifacts. Unreal migration, PIE, and
cold-copy checks stay `NOT_RUN` until their declared contexts supply evidence.

## Final Response

Report profiles/versions, dependency classification, changes and replacements,
material/reference/world/collision findings, target and cold-copy checks, HIL
result separately, evidence, NOT_RUN items, risk, backup, and rollback.
