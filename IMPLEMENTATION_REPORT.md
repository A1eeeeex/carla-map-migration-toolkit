# Implementation report

Date: 2026-08-26 (Asia/Shanghai)

## Route and Profile scope

The implementation keeps exactly three top-level Skills:

1. RoadRunner to Source CARLA: `roadrunner-datasmith`, experimental
   `roadrunner-filmbox`, and limited `generic-fbx-xodr`; `standard` and
   `large-tiled` are distinct map modes.
2. Source CARLA to Package CARLA: `content-package` and
   `full-carla-package` with a hard platform-match gate.
3. Source CARLA to vanilla UE4.27: `standalone-map` and experimental
   `hil-ready`, with second clean-project cold-copy as an acceptance gate.

Repair, validation, performance, safety, schemas, profiles, and templates are
shared Plugin resources rather than additional top-level Skills.

## Read-only discovery and baseline

The discovery phase read the existing legacy Skill, 17 Python sources (2,804
lines), the available historical performance material, the frozen handoff docs,
and environment metadata without running Unreal/CARLA mutations.

Observed environment facts were Source CARLA 0.9.16 at a dirty detached source
checkout using the CARLA UE 4.26.2 fork, Package CARLA client distributions
matching 0.9.16, and vanilla UE 4.27.2. The RoadRunner/exporter version remains
unknown. These are environment observations, not current-toolkit route results.

The migration matrix classifies the 17 legacy scripts as 10 WRAP, 5 SPLIT,
1 REWRITE, 1 ARCHIVE, and 0 KEEP-AS-IS. No legacy source was copied because
publication rights are unknown and map-specific hardcoding is extensive.

Local-only discovery evidence is under `development/local/analysis/`, including
the source inventory, behavior baseline, script matrix, hardcode/secret scan,
compatibility evidence, open questions, publication-rights register, dependency
map, and phased plan. It is deliberately excluded from Git publication.

## Implemented shared core

- Canonical path resolution, allowed-root containment, and execution-context
  fast failure.
- Stable JSON errors, status aggregation, UTC stage evidence, and atomic artifact
  writes with a no-clobber race-safe path.
- Workspace shape checks, route/profile/version inspection, immutable plan hash,
  explicit RoadRunner/XODR or downstream handoff/inventory fingerprints, and
  stale workspace/input detection.
- Tar/zip inspection without extraction, including absolute/traversal/link,
  duplicate-member, expanded-size, and required-member checks.
- Explicit timestamped ordinary-file backups with SHA-256 manifests; empty
  backups and raw host backup of Unreal binary assets are blocked.
- Public-report redaction helpers for emails, network addresses, common local
  paths, secret assignments, and caller-supplied private identifiers.
- Complete comparable-condition performance checks and validated protected
  LOD0/material-slot/transform/collision/XODR SHA-256 evidence.
- Read-only pending validation reports that preserve `NOT_RUN` when no
  Editor/runtime evidence exists.

The host core intentionally does not pretend to implement Unreal API migration,
CARLA runtime probes, Cook/import, or cold-copy. Those context adapters require
authorized real environments and remain explicit gaps.

## Shared contracts and public material

- Six JSON Schema 2020-12 contracts with anonymous examples.
- Machine-readable reason code and profile catalogs.
- Three thin Skills with route-local contracts and shared workflow, context,
  repair, safety, performance, and evidence references.
- 73 static trigger prompts meeting per-Skill direct, indirect, adjacent-negative,
  out-of-scope, and ambiguous coverage; 12 behavior safety cases.
- Ten anonymous text-only fixture families.
- English/Chinese README, route docs, compatibility policy, local marketplace,
  and hosted L0–L2 CI definition.
- An exact per-file publication allowlist and automated binary/asset, host-path,
  secret-assignment, and configured-identifier gates.

## Rollback

The initial handoff directory was not a Git repository. The verified candidate
was later recorded as the local Git baseline commit `b44c514`; the original
scaffold hashes remain at the Git-ignored local path
`development/local/analysis/implementation-baseline.sha256`.

Repository changes can be reviewed or reverted from that baseline without
touching `development/local/` or any external environment. Do not use `git
clean`, `git reset --hard`, recursive workspace deletion, or raw Unreal asset
operations. Runtime write adapters, when added, must use their own timestamped
backup manifest and verified reverse operation.
