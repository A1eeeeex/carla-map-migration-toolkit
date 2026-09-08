# Three-route verification: decision brief

Status: route coverage and exact Primary Profile stacks are decided.

## Release decision

`v0.1.0-rc` requires Route Coverage: one accepted Primary Profile for every
supported Migration Route. Complete Profile Coverage is not required.

| Route | Primary Profile | Required level | Recovered historical evidence |
|---|---|---:|---|
| RoadRunner -> Source CARLA | `roadrunner-datasmith` | L4 | Post-import asset, material, reference and saved-state checks pass; current-contract replay remains required. |
| Source CARLA -> Package CARLA | `content-package` | L5 | Package archive, safety, XODR, 50-file install parity, runtime-domain checks and archive hash continuity are present. |
| Source CARLA -> vanilla UE4.27 | `standalone-map` | L5 | Target/collision/visual checks and a cold-copy archive with matching candidate/copy map hashes are present. |

Implementation may still start with Source CARLA to UE4.27 because its current
L2 slice is most mature. That ordering does not lower the release gate for the
other routes.

## Locked replay identities

The replay rejects vague or dirty version identities. Its locked stack is:

| Route | Locked stack | Run-bound identity still required |
|---|---|---|
| RoadRunner -> Source CARLA | RoadRunner R2025a built-in Datasmith export and integration bundle 1.4.4 -> CARLA `0.9.16` / modified UE `4.26.2` | Rights-safe export and source-project fingerprints. |
| Source CARLA -> Package CARLA | Source CARLA `0.9.16` -> matching Linux x86_64 Package CARLA `0.9.16` client/server pair | Source handoff, target baseline and package artifact fingerprints. |
| Source CARLA -> vanilla UE4.27 | CARLA `0.9.16` / modified UE `4.26.2` -> vanilla UE `4.27.2` | Primary and second clean-project fingerprints. |

Every replay also records the exact Toolkit commit, OS/GPU/driver fingerprint
and Rights-safe Replay Input identity. Dirty or vague identities cannot support
a public compatibility claim.

The CARLA 0.9.16 Linux guide states that this release uses a modified Unreal
4.26 fork and documents Ubuntu 20.04/22.04. Epic's UE4.27 documentation lists
Ubuntu 18.04 for Linux development. Therefore the final run must report the
actual OS as observed evidence and must not imply broad official Linux support.

Primary sources:

- <https://carla.readthedocs.io/en/0.9.16/build_linux/>
- <https://github.com/carla-simulator/carla/releases/tag/0.9.16>
- <https://dev.epicgames.com/documentation/en-us/unreal-engine/hardware-and-software-specifications?application_version=4.27>

## Required execution contexts across the routes

| Context | Responsibility |
|---|---|
| `host-cpython` | Workspace validation, input hashing, dependency-plan sealing, evidence aggregation and redaction checks. |
| `source-unreal-python` | Source Asset Registry inventory, referencers, material/class/world/collision baselines and approved migration export. |
| `ue427-unreal-python` | Target migration, dependency localization/replacement, redirector/reference/material/world/collision audits, and cold-copy audits. |
| `carla-client-python` | Source and Package CARLA runtime, map, spawn, traffic and dynamic smoke checks with an exact client/server match. |
| `shell-build` | Version-resolved Cook/package/import commands and build evidence. |
| UE4.27 Editor/PIE | Primary target reopen, visual and collision smoke evidence at L3/L4. |
| second clean UE4.27 project | Independent reopen, dependency, PIE, visual and collision evidence at L5. |

No host command may substitute for an Unreal execution context.

## Historical evidence boundary

The recovered records corroborate the maintainer's statement that all three
routes were exercised. They are useful characterization and contain real hash
continuity, but they do not use the current `verified-run` schema or bind every
required stage to the current Toolkit commit. They must not be copied into the
public repository or relabelled as Current-toolkit Verified Runs.

The historical binding is complete: 15 checks have direct historical support,
20 have partial support and 6 have no safe match. All 41 still require current
contract evidence because Toolkit identity, execution context, stage provenance
or rights-safe evidence is missing.

## Current environment status

Read-only discovery found the exact CARLA `0.9.16` release checkout and
executable UE `4.26.2` and `4.27.2` Editors outside the repository. This changes
the environment status from absent to `FOUND_NOT_ACCEPTED`, but does not prove a
usable replay stack:

- all three Git worktrees contain tracked changes;
- the Source tree also contains many untracked files whose rights and role were
  deliberately not inspected;
- 17 Unreal projects are discoverable in the scoped roots, but no current
  `map-workspace.json`, accepted `map-handoff.json`, selected target project or
  selected second clean project exists;
- no UE or CARLA executable is currently running;
- exact engine commits and sanitized component fingerprints are published in
  the stack lock; absolute paths and private content remain local-only.

The newest Downloads ZIP passed structural archive checks and contains no map
assets or engine/runtime binaries, but its code and documentation contain no
CARLA, Unreal, RoadRunner, Codex Plugin or migration-contract signal. It also
contains generic absolute-path and IP-like indicators. It is excluded from this
toolkit and was not extracted.

Environment acceptance therefore requires either clean, reproducible external
checkouts or a reviewed explanation and hash of every local modification, plus
an explicit Source project, primary target, second clean project and
rights-cleared map input.

## Decision sequence

1. Confirm one Rights-safe Replay Input that can exercise all three paths.
2. Implement only missing current-context adapters and replay the gaps without
   skipping L3, L4 or L5 gates.
