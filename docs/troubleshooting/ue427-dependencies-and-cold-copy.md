# UE4.27 migration or clean-project copy has broken references, materials or collision

## Symptoms

CARLA classes remain in vanilla UE4.27, or the producer opens correctly while the second project has missing materials, broken lighting or no road collision.

## What usually needs checking

Separate dependency-plan completeness from actual Asset Registry findings. Check exact case-sensitive package paths, dependency closure, parent materials/textures, World Settings, shader progress and Content/Content nesting.

## Toolkit diagnosis

From the installed clone in host-cpython; replace every angle-bracket value
with your own permitted local input before running:

```bash
CMTK_EXECUTION_CONTEXT=host-cpython .venv/bin/python plugins/carla-map-migration-toolkit/scripts/cmtk.py inspect --route source-carla-to-ue427 --config <workspace.json>
CMTK_EXECUTION_CONTEXT=host-cpython .venv/bin/python plugins/carla-map-migration-toolkit/scripts/cmtk.py content-audit --target <delivery.tar.gz-or-directory> --allowed-root <input-root> --asset-root MAPS/Example --map-name ExampleMap
```

UE427-DEPENDENCY-UNKNOWN or UE427-REPLACEMENT-UNDEFINED blocks an incomplete dependency action plan. DELIVERY-CONTENT-INCOMPLETE flags a missing named map or invalid Content layout. The host only evaluates the supplied dependency manifest and file structure; it cannot discover binary references by reading asset bytes.

## Manual / Editor checkpoint

In ue427-unreal-python use Asset Registry/referencers and approved Migrate/AssetTools operations. Localize or replace dependencies with a backup. Close the producer before hashing; transfer the complete approved payload at unchanged paths into a separate clean target. Never use OS renames/deletes on individual Unreal assets.

## Validation

In the receiver, reopen the exact map, audit disallowed references, allow shader warmup, check materials/daylight, PIE and drivable collision. Archive/per-file parity supplements these checks; it cannot pass cold-copy by itself.

## Evidence to keep

Producer and receiver identities, dependency/action inventory, material/world/collision observations, target and receiver checks, delivery hashes and reviewed captures.

## What this guide does NOT prove

No automatic removal of all CARLA classes, general Unreal repair or transfer of CARLA server/sensor/Traffic Manager behavior. An opened viewport is not complete L5 acceptance.

Based on the repository's [operation reference](../../plugins/carla-map-migration-toolkit/references/ue427-content-delivery.md),
[reason codes](../../plugins/carla-map-migration-toolkit/references/reason-codes.md)
and existing host/fixture checks. [Back to cookbook](README.md).
