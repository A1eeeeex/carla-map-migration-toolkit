# RoadRunner import finishes but assets or materials are incomplete

## Symptoms

Dataprep shows a populated preview, but the saved map is empty, has black materials or loses references after reopening.

## What usually needs checking

Distinguish Import, Execute, Commit and Save. Confirm exporter profile and referenced sidecars; check the persistent level, dirty packages, saved asset paths, shader progress, material parents and textures.

## Toolkit diagnosis

From the installed clone in host-cpython; replace every angle-bracket value
with your own permitted local input before running:

```bash
CMTK_EXECUTION_CONTEXT=host-cpython .venv/bin/python plugins/carla-map-migration-toolkit/scripts/cmtk.py inspect --route roadrunner-to-source-carla --config <workspace.json>
CMTK_EXECUTION_CONTEXT=host-cpython .venv/bin/python plugins/carla-map-migration-toolkit/scripts/cmtk.py verify-plan --config <workspace.json> --plan <route-plan.json> --plan-sha256 <sealed-hash>
```

RR-EXPORT-MEMBER-MISSING means expected export members are absent. PLAN-HASH-MISMATCH or stale input/workspace checks require a fresh reviewed plan, not editing a hash. Neither command inspects compiled materials or confirms Dataprep Commit.

## Manual / Editor checkpoint

In source-unreal-python/Editor inspect committed assets and referencers. Save and reopen before calling import complete. Wait for shader compilation; repair missing parents/textures via Unreal APIs only after a bounded plan and backup.

## Validation

Reopen the exact saved map, verify representative material views and reference closure, then collision and alignment. Repeat affected checks after repair rather than reimporting everything blindly.

## Evidence to keep

Export inventory, checkpoint outcomes, saved asset counts/paths, dependency observations, sanitized compile diagnostics, before/after views and rollback metadata.

## What this guide does NOT prove

A host input check cannot certify a RoadRunner export, diagnose every black material or prove that the editor saved a working map.

Based on the repository's [operation reference](../../plugins/carla-map-migration-toolkit/references/carla-map-operations.md),
[reason codes](../../plugins/carla-map-migration-toolkit/references/reason-codes.md)
and existing host/fixture checks. [Back to cookbook](README.md).
