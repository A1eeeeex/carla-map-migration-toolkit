# Source import and Package CARLA operations

Read this for an import/save problem or a Source-to-Package delivery. It is
shared guidance, not a fourth route and not an automatic importer.

## Source import: establish what actually exists

1. In `host-cpython`, inventory the export, map basename, XODR, sidecars and
   hashes. Resolve the source checkout's importer and supported export profile;
   do not feed Datasmith to a legacy FBX importer.
2. In `source-unreal-python`, distinguish Dataprep preview from committed
   assets. Inspect the Import / Execute / Commit / Save checkpoints, persistent
   level, generated asset paths, dirty packages and actual disk-backed saves.
   A populated preview viewport is not proof of a saved map.
3. Inspect dependencies and referencers before repairs. Reopen the saved map,
   check material parents/textures, collision and scale, and sample the XODR
   waypoints against road geometry. Check basename, export revision, origin,
   axis conventions, units and transforms before changing geometry or XODR.
4. Confirm spawn, route/traffic actors and pedestrian navigation only where
   the chosen profile requires them. Save an explicit functional baseline.
   Continue with [performance operations](map-performance-operations.md) only
   if requested and that baseline passes.

## Package: trace the whole chain

Use the checked-out build scripts and matching CARLA documentation for the
exact version. Source build packaging and a binary distribution's import
script are different operations. `make package` and `ImportAssets.sh` are
possible entrypoints, not portable commands to run without inspection.

Before cooking, inspect Package JSON, the map package path, MapsToCook or the
version's equivalent, XODR staging, saved dependencies and redirectors. If that
version uses a `props` list for mesh reachability, it describes actual static
meshes, not materials or arbitrary files. Do not populate it indiscriminately.
Use Cook logs and the Asset Registry to diagnose missing soft dependencies.

Run the following from an installed repository root in `host-cpython`:

```bash
CMTK_EXECUTION_CONTEXT=host-cpython .venv/bin/python plugins/carla-map-migration-toolkit/scripts/cmtk.py map-package-audit --target <archive-or-staging-tree> --allowed-root <input-root> --allowed-root <report-root> --map-name ExampleMap --output <report-root>/package-audit.json
```

The audit accepts tar/zip or a staging directory. It checks unsafe members,
duplicate paths, expansion limits, an unambiguous named map and matching XODR.
For a Cook profile known to emit a separate map `.uexp`, add
`--require-cooked-sidecars`; `.ubulk` is not mandatory for every asset.
An expected archive digest can be checked with `--expected-sha256`.
Mesh/material/texture folder labels are hints, not asset-class or dependency
proof. Missing hints produce `WARN`, even if the map and XODR are present.
This command never extracts, imports, cooks or starts a server.

## Diagnose in order

| Symptom | First discriminating check |
|---|---|
| Map absent from available maps | Cook output, package path, install/import result and exact server installation |
| World loads but looks empty | Asset count/dependency closure, then spectator position and streaming; world-load success alone is insufficient |
| Source looks right; package loses materials | Cook reachability, saved parents/textures, soft references and package versions |
| Road and waypoints disagree | Matching export/hash, XODR basename, origin/axes/units and transforms |
| Vehicle falls or traffic cannot initialize | Drivable collision, spawn height, XODR topology and required route/traffic actors |
| Startup fails or performance is erratic | Free disk/RAM/VRAM, active editors/servers and port ownership before retrying |

Wait for adequate VRAM before a heavy launch. Do not kill unrelated processes
or start a second server to work around a busy one. Use a matching CARLA client
in `carla-client-python`, then collect registration, load, visual, collision,
XODR/spawn and a bounded dynamic smoke test in one planned session. Do not
repeat the complete runtime suite for a report-only or documentation change.

Back up an authorized same-name target before replacement. Archive structure
is L1 evidence only; independent Package runtime and portability evidence are
still required by the route contract. Preserve failed results and rollback.
