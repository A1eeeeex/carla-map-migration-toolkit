# UE4.27 Content-only delivery

Use within `source-carla-to-ue427`, including a CARLA-origin map already native
to UE4.27. Resume at delivery when its earlier migration evidence exists; do
not force another Source import just to audit an archive. Unknown provenance
does not prevent read-only structure inspection, but does prevent claiming
complete route acceptance. Generic unrelated Unreal projects are out of scope.

## Freeze the delivery contract

Record the exact UE4.27 patch, map package path, case-sensitive asset root,
intended collision/lighting profile and approved dependencies. For example:

```text
Delivery archive
└── Content/
    └── MAPS/Example/
        ├── ExampleMap.umap
        ├── MESH/...
        ├── MATERIAL/...
        └── TEXTURE/...

Map package: /Game/MAPS/Example/ExampleMap
```

This is an example, not a required rename. Preserve the user's established
mount path and layout. Keep README, SHA256 and manifest beside the archive,
not inside its Content tree. Do not include a `.uproject`, Plugins, Config,
Saved, Intermediate, DerivedDataCache, binaries or engine assets. A different
delivery profile may require a different contract; do not silently relax this
strict Content-only audit.

## Producer workflow

1. In `ue427-unreal-python`, inspect map dependencies and referencers. Migrate
   the map's dependency closure into a clean UE4.27 staging project using
   Unreal's Migrate/AssetTools workflow. Localize approved references and fix
   redirectors through Unreal APIs, with a reviewed plan and rollback point.
2. Save all packages, reopen and check missing classes/materials, World
   Settings, visuals and intended collision. Wait for shader compilation
   before interpreting a transient black/grey material as a missing asset.
3. Close the producer before inventory and hashing. Create a content-preserving
   archive of the approved tree without renaming, moving or deleting individual
   Unreal assets through the OS. Do not overlay a previous delivery blindly.
4. Audit and generate a manifest using the host commands below. An existing
   report is not overwritten. Repeated `--allowed-root` flags permit separate
   input and report directories without granting an entire home or mount root.

```bash
CMTK_EXECUTION_CONTEXT=host-cpython .venv/bin/python plugins/carla-map-migration-toolkit/scripts/cmtk.py content-audit --target <delivery.tar.gz-or-directory> --allowed-root <input-root> --allowed-root <report-root> --asset-root MAPS/Example --map-name ExampleMap --output <report-root>/content-audit.json
CMTK_EXECUTION_CONTEXT=host-cpython .venv/bin/python plugins/carla-map-migration-toolkit/scripts/cmtk.py delivery-manifest --content <staging-project>/Content --map-package /Game/MAPS/Example/ExampleMap --engine-version 4.27.2 --allowed-root <staging-project> --allowed-root <report-root> --output <report-root>/delivery-manifest.json
```

`content-audit` accepts the Content directory itself, its delivery parent or
a tar/zip archive. It requires the exact map, the selected asset root and no
double `Content/Content`, project/cache files, links or special members. It
counts regular assets, checks size limits and optionally an archive SHA256;
it never extracts or interprets binary asset references. `delivery-manifest`
requires the specified map to exist and emits sorted relative paths, sizes,
per-file SHA256, engine version and map package. It rejects non-package files,
links and observed changes while hashing. Neither command proves dependency
closure or a successful editor open; `runtime_validation` remains `NOT_RUN`.

## Receiver and cold-copy

Use a second blank project on the declared vanilla UE4.27 version. With the
editor closed, transfer the complete approved Content payload into the project
Content directory at the same package paths, using the authorized delivery
workflow; do not create Content/Content. Do not use OS operations to rename,
move or delete internal assets. Inspect and back up any conflicting target
before replacement, or use a new empty target. Verify delivered hashes before
opening the exact map package.

In one consolidated acceptance session, allow shader warmup, reopen, inspect
external references/logs, test PIE, the agreed viewpoints and collision.
Repeat only failed or affected checks after a repair. Hash equality alone
cannot pass cold-copy, and a producer screenshot cannot prove receiver success.
Record the target identity and observations through the existing route
evidence adapters; the two new diagnostic reports are not stage receipts.

## Black materials, strange weather and incomplete deliveries

Investigate in this order: shader progress and logs; exact package path/case;
missing texture or parent material; external project/plugin references;
texture virtual-streaming and material sampler compatibility; engine version;
archive/per-file hash mismatch. Repair through Unreal APIs and recheck the
affected material plus a representative view, rather than recooking everything.

For daylight, inspect existing sky/light actors, exposure, fog, post-processing
and defaults in the receiving project. Do not copy CARLA weather-blueprint
values blindly into a different actor class or intensity unit. Plan a bounded
lighting change, preserve its originals and compare the same camera view.
Never remove required collision to improve a visual-only benchmark while
claiming a simulation-ready delivery. A road-only collision or daylight-only
profile must be named explicitly, including what it does not preserve.
