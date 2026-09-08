# CARLA custom-map troubleshooting

Start with the symptom, not a full migration replay. These guides distinguish
host diagnostics from real Editor/runtime validation; they do not replace the
version-specific CARLA map import and packaging workflows.

| Symptom | Guide |
|---|---|
| Visible roads, missing waypoints, wrong XODR identity or alignment | [Topology and XODR](topology-and-xodr.md) |
| RoadRunner import preview exists but saved assets/materials are incomplete | [Import checkpoints](roadrunner-incomplete-import.md) |
| Map missing after Cook, bad archive or wrong packaged map/XODR | [Package map and archive](package-map-missing.md) |
| CARLA dependencies remain, or UE4.27 cold-copy loses references/materials/collision | [UE4.27 dependency and delivery checks](ue427-dependencies-and-cold-copy.md) |
| Optimization makes frame time or secondary metrics worse | [Performance regression](performance-regression.md) |

## Before running a command

Complete [installation](../installation.md). Commands use the repository-local
Python interpreter and `CMTK_EXECUTION_CONTEXT=host-cpython`; there is no assumed
globally installed `cmtk` executable. Replace angle-bracket placeholders before
execution: they are not literal shell syntax. Allowed roots must be narrow,
existing, authorized directories. Never grant an entire home or mount root.

Host CLI exit codes: 0 can mean PASS **or WARN**, 2 means FAIL/BLOCKED, 3 means
NOT_RUN. Read the JSON status, checks and reason codes, not only the exit code.
`validate` creates a pending report, not engine execution. Archive/Content
commands inspect without extraction; `--output` writes a new report under allowed roots.

## Report a reproducible issue

Use the [contribution guide](../../CONTRIBUTING.md) and compatibility form.
Include exact versions, route/Profile, command, reason code and a short sanitized
excerpt. Do not upload customer maps, credentials, private XODR or full raw logs.
