# CARLA map loads but topology or waypoints are missing

## Symptoms

The road is visible but waypoint sampling, spawn placement or a bounded drive does not match it. The loaded map and XODR may come from different export revisions.

## What usually needs checking

Compare map basename, XODR identity/hash, export revision, origin, axes, units and transforms. Confirm the actual server world and matching client; do not edit road geometry to hide an identity mismatch.

## Toolkit diagnosis

From the installed clone in host-cpython; replace every angle-bracket value
with your own permitted local input before running:

```bash
CMTK_EXECUTION_CONTEXT=host-cpython .venv/bin/python plugins/carla-map-migration-toolkit/scripts/cmtk.py inspect --route roadrunner-to-source-carla --config <workspace.json>
```

Expect named path/profile/export checks. SOURCE-XODR-MISSING or RR-EXPORT-MEMBER-MISSING blocks incomplete inputs. A PASS does not parse or validate OpenDRIVE topology, and this inspection does not guarantee a basename match: compare identities explicitly. For a Package archive use the named-map audit in the packaging guide.

## Manual / Editor checkpoint

In source-unreal-python inspect saved transforms and road geometry. In carla-client-python use the matching server/client to record map identity, topology, sampled waypoints and spawn points. Only after alignment checks, run a bounded drive. Keep elevated-road/slope scope explicit.

## Validation

Recheck the same revision and sampled locations after an approved repair; validate collision and required traffic/navigation separately. Missing required runtime observations stay NOT_RUN.

## Evidence to keep

Input and XODR hashes, map identity, versions, topology summary, sample positions, collision/drive observations and the exact sampling scope. Publish sanitized summaries, not customer XODR.

## What this guide does NOT prove

No automatic OpenDRIVE repair, general conformance certificate or guarantee for elevated roads. A visible road is not topology evidence.

Based on the repository's [operation reference](../../plugins/carla-map-migration-toolkit/references/carla-map-operations.md),
[reason codes](../../plugins/carla-map-migration-toolkit/references/reason-codes.md)
and existing host/fixture checks. [Back to cookbook](README.md).
