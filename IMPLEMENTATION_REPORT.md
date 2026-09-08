# Implementation report

Date: 2026-09-01 (Asia/Shanghai)

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
matching 0.9.16, and vanilla UE 4.27.2. At Phase A closeout, the
RoadRunner/exporter version remained unknown. Read-only follow-up on 2026-08-28
locked it to RoadRunner R2025a, its built-in Datasmith export identity and an
external integration bundle at 1.4.4. These are environment observations, not
current-toolkit route results.

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
- A local-only adapter-receipt schema, Python 3.7-syntax-compatible
  standard-library context finalizer, and host recorder for the four external
  contexts. They bind observations to the sealed plan/stage, live API/version,
  hashes, public paths, private sensitive-term scan and atomic stage/check
  evidence without executing the migration operation itself.
- Optional stage contracts for repair and optimization across all three routes.
  Repair PASS requires the six DETECT/EVIDENCE/PLAN/APPLY/VERIFY/ROLLBACK
  observations; optimization apply PASS requires a functional baseline,
  protected-property non-regression and rollback readiness.

The core intentionally does not pretend to implement Unreal API migration,
CARLA runtime probes, Cook/import, or cold-copy operations. It records their
context-bound receipts, while route-specific operation collectors still require
authorized environments.

On 2026-09-01, one authorized private collector exercised the current
`ue427-unreal-python` finalizer and host recorder against vanilla UE4.27.2. The
first candidate was withdrawn after strict log review found 352 material
parameter errors caused by a virtual-texture type mismatch. Read-only probing
reduced the repair scope to eight 4096×4096 textures referenced by four material
instances. A sealed Unreal-API apply changed only their
`virtual_texture_streaming` property, retained a metadata rollback, copied no
assets and preserved the project, map, configuration and XODR hashes.

A fresh Vulkan RenderOffScreen session then confirmed 605 expected assets, zero
missing assets, zero material/type/compiler errors, five Editor and five PIE
road-collision samples, fresh target reopen, 9,438 static-mesh actors and a
180-frame PIE smoke with no asset writes. All five 1600×900 fixed views passed
paired quantitative and non-automated visual review. The six-check receipt was
finalized against the live UE4.27.2 API and host-recorded into a private,
authoritative-sensitive-term-scanned stage candidate. It is not promoted under
`evidence/verified/` because the route's current Source-side provenance and L5
cold-copy remain incomplete. Private map identity, paths, screenshots, logs and
binaries remain excluded.

The same authorized target then supplied a fresh post-repair matched Stage-A LOD
diagnostic. A semantic rollback established the repaired no-LOD baseline, the
candidate was reapplied through Unreal APIs, and both states used five views,
three repeats and 300 selected frames per repeat under the same 640×372 Low
offscreen protocol. The 52 selected meshes retained LOD0, material-slot,
transform and collision protections. Across 4,500 selected frames per state,
average FPS improved 4.28%, mean frame time improved 4.10%, p95 improved 15.57%
and GPU mean time improved 15.83%; primitives fell 75.06% while draw calls rose
15.82%. Median frame time improved only 0.56%, below the sealed automatic 3%
threshold, so the 29-check postflight correctly reports `REVIEW_REQUIRED`.
This remains one-host Editor diagnostic evidence, not a packaged-runtime,
general-map or L5 claim.

The public rights-safe quickstart generates an anonymous text-only
RoadRunner-shaped fixture in an explicit empty temporary directory. It exercises
host inspection, plan sealing, plan verification and the expected `NOT_RUN`
runtime safe stop without committing a map, XODR, Unreal asset or binary. It is
L1 behavior evidence, not a substitute for a real Editor replay fixture.

Release review then closed two fail-open reporting gaps. External receipts now
must contain every required check for their stage, bind each PASS/FAIL to one
matching boolean acceptance observation and suppress next-stage transitions on
failure. The existing six-check real target receipt passed the stricter recorder
without rerunning Unreal. The publication audit now rejects forbidden asset
paths anywhere in reachable Git history and blocks binary blobs or binary
external artifacts that cannot be completely text-scanned.

## Phase A continuation

- Frozen public claims, non-claims, support-state semantics, route acceptance,
  proof levels and Claim→Test→Evidence traceability.
- Added machine-readable Claims Registry and Verified Run contracts. A
  maintainer/community compatibility entry must cite a verified run and evidence
  path, and publication tests resolve that reference to a matching record.
  Source→UE4.27 PASS requires the complete 15-check L5 contract with non-empty
  structured check evidence, environment, hashes, contract-stage results, exact
  redaction coverage and rehashed input/artifact bytes from one read snapshot.
  Required checks bind proof-capable evidence types and positive acceptance
  assertions, while stage metadata and read/write/backup paths bind to the
  fingerprinted route workspace.
- Added host-only Source→UE4.27 dependency classification and plan integration.
  Unknown, blocked, duplicate, incomplete or strategy-less executable
  dependencies block the sealed plan; an empty dependency fact source also
  blocks rather than proving completeness. Classification actions and their
  SHA-256 fingerprint now come from one captured byte snapshot.
- Added a rights-gated, text-only Golden Map plan with eight fault variants; no
  XODR, Unreal asset or private map content was added.

## Shared contracts and public material

- Eleven JSON Schema 2020-12 contracts with anonymous examples.
- Machine-readable reason code and profile catalogs.
- Three thin Skills with route-local contracts and shared workflow, context,
  repair, safety, performance, and evidence references.
- 73 static trigger prompts meeting per-Skill direct, indirect, adjacent-negative,
  out-of-scope, and ambiguous coverage; 12 behavior safety cases.
- Eleven anonymous text-only fixture families.
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
