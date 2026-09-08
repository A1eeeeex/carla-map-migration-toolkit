# Golden Map input contract

Status: awaiting maintainer input. Supply one route at a time; completing all
three is not a prerequisite for inspecting the first. Keep map assets outside
this repository in a dedicated, explicitly allowed workspace. This directory
contains the protocol, not an asset drop folder.

## Identify the input

Record a public-safe map alias, revision/hash, owner, redistribution permissions,
route, source/target Profile, OS/architecture and exact tool versions. Keep the
alias-to-private-name mapping local. Use the existing
[workspace schema and example](../../../../plugins/carla-map-migration-toolkit/examples/map-workspace.example.json);
do not invent another workspace format. Replace its illustrative paths locally.

| Starting point | Supply locally | Evidence needed for its result |
|---|---|---|
| RoadRunner | Datasmith + matching XODR + referenced textures/meshes; for supported FBX profile include required sidecars; exporter/version and optional source-project identity | Saved map identity, Source CARLA/UE versions, material/reference/collision checks, topology summary, sampled waypoints, spawn points, runtime load and bounded drive |
| Source CARLA to Package | Source handoff, asset/dependency/route inventories, matching XODR, build/target platform and version | Named cooked map, package layout/hash, matching XODR, independent runtime load and bounded drive |
| Source CARLA to UE4.27 | Source handoff and dependency/action inventory, clean target identity and a separate cold-copy project | CARLA dependency audit, materials/references/collision/daylight, target reopen/PIE, cold-copy reopen/PIE, Content-only archive/hash parity |

A screenshot or an editable project alone is not a complete Source handoff.
Missing evidence can allow read-only inspection but blocks promotion to a
complete Verified Run. See [route acceptance](../../../../docs/acceptance-contracts.md).

## Intended small-map design

Retain the planned 600–1,200 m network, curve, junction, slope change, 8–20 spawn
points, drivable collision, two or more material classes and basic environment
from [manifest.json](manifest.json). Record deviations before testing; do not
silently substitute a flat-road case for slope coverage. Fault variants are
separate disposable copies, one primary fault each, never the release candidate.

## Intake decision

Check [rights](RIGHTS_CHECKLIST.md), archive safety, identity and available
disk/RAM/VRAM. Unknown rights stop public sharing; unknown versions/dependencies
stop affected writes. Record absent route results as NOT_RUN, not failures that
must be worked around. No engine launch is needed merely to inventory a delivery.
