# Verification status

Date: 2026-09-05 (Asia/Shanghai)

## Current release-preparation update

- The September 5 integration passed 435 host/fixture/structure tests and all
  three Skill validators; production code is unchanged in this documentation/
  installation closeout. New delivery/metric helpers are included.
- A real Content-only archive audit found 634 UE assets; existing performance
  summaries were compared over 16 counters without hiding regressions.
- Later September 1 records include Source flat-road driving, a second clean
  UE4.27.2 project's structural checks, and subsequent PIE/sunny-view/Content
  delivery results. The older blanket NOT_RUN statements below describe an
  earlier implementation snapshot, not absence of that later real work.
- CLI 0.148.0 failed before the default model could run. A task-local Codex CLI
  0.153.4 passed all 11 changed-description/previous-failure routing cases.
  This was one description-based batch, not a full current 83-case installed-use
  evaluation. Earlier full routing work had 72/73 passes; retain that failure
  rather than rewriting its historical result.
- Current installation/targeted-check and snapshot/privacy results are in the
  [release checklist](docs/release-readiness.md). No engine or CARLA server is
  launched for this closeout; no complete Verified Run is manufactured.

## Earlier implementation snapshot (2026-09-01)

The following history predates the later reimport/second-project records
summarized in [current status](docs/current-status.md).

## Scope and environment

- Routes: RoadRunner → Source CARLA; Source CARLA → Package CARLA; Source
  CARLA → vanilla UE4.27.
- Profiles: `roadrunner-datasmith`, experimental `roadrunner-filmbox`, limited
  `generic-fbx-xodr`, `source-carla-map`, `content-package`,
  `full-carla-package`, `standalone-map`, and experimental `hil-ready`.
- Host: Ubuntu 22.04, Linux x86_64, host CPython.
- Observed Source CARLA: `0.9.16-dirty`, commit
  `294096eb1c38eabf246e4f3a9cdab704e33a7f4c`, CARLA Unreal fork 4.26.2.
- Observed Package CARLA Python distributions: 0.9.16.
- Observed target engine: vanilla Unreal Engine 4.27.2.
- Observed RoadRunner export identity: RoadRunner R2025a, built-in Datasmith
  export with scene version 0.24 and SDK version 4.26.1; external integration
  bundle 1.4.4.

These are environment observations, not compatibility PASS claims.

## Evidence by level

| Level | Status | Evidence |
|---|---|---|
| L0 structure | PASS | Canonical Plugin validator and all three canonical Skill validators passed. Eleven schemas, examples, profiles, manifests, claims and links are covered by tests. |
| L1 pure logic | PASS | The full host-side test suite and Ruff checks passed; exact closeout commands and counts are recorded below. |
| L2 anonymous fixtures | PASS | Eleven text-only fixture families plus four execution-context boundary fakes cover route, dependency classification, archive, performance, schema, safety, CLI and adapter behavior without real map or engine assets. |
| L3 Editor | PASS (current target stage only) | After a bounded eight-texture repair, a fresh UE4.27.2 replay passed reopen, inventory, strict material-log and five fixed-view checks. Source Editor remains `NOT_RUN`. |
| L4 runtime | PASS (current target stage only) | The same replay passed one 180-frame PIE smoke and five Editor plus five PIE sampled road-collision traces. Package CARLA/CARLA Python API remains `NOT_RUN`. |
| L5 portability | NOT_RUN | No second clean-project UE4.27 cold-copy replay was run. |

## Closeout commands

The following commands ran against the final implementation sources:

```text
python3 .../plugin-creator/scripts/validate_plugin.py plugins/carla-map-migration-toolkit
  PASS — Plugin validation passed
python3 .../skill-creator/scripts/quick_validate.py <each of three Skill directories>
  PASS — Skill is valid! (3/3)
python3 -m ruff check --no-cache plugins/carla-map-migration-toolkit/scripts/cmtk tests demo/quickstart development/shared/release_tools
  PASS — All checks passed!
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  python3 -m pytest -q -p no:cacheprovider
  PASS — 379 passed
```

The full pytest result includes the exact-file publication allowlist scan, all
eleven schema/example checks, Claims/Verified Run and cross-reference gates,
Source→UE4.27 dependency classification, 73 static trigger cases, 12 behavior
cases, CLI integration tests, the rights-safe quickstart, four external-context
receipt finalization branches, three-route repair/optimization contracts, and
unit tests.

Two intermediate full-suite runs reported `218 passed, 2 failed`: the new
publication gate correctly detected generated `.pyc` files. The first run placed
official validators before pytest; the second exposed one CLI subprocess test
that replaced rather than inherited the bytecode-suppression environment. The
test harness now preserves the environment, generated caches were removed, and
the final clean rerun above passed. No product failure was hidden or reclassified.

A later 2026-09-01 invocation that accidentally omitted
`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` failed before collection when a system ROS
`launch_testing` plugin imported its unavailable `lark` dependency. The
repository-isolated command shown above was rerun immediately and passed all
361 tests in 21.55 seconds. After adding the rights-safe quickstart and strict
evidence/publication regressions, the current implementation rerun passed all
379 tests in 6.21 seconds.

## Additional NOT_RUN items

- Model-based Skill trigger precision/recall/confusion evaluation: `NOT_RUN`.
  Static dataset shape and expected-route assertions run at L1 only.
- Hosted GitHub Actions L0–L2 execution: the pre-Phase-A `main` run passed. The
  current Phase A change is intentionally not pushed under the supplied master
  prompt, so hosted CI for this change is `NOT_RUN`.
- A disposable allowlisted candidate-snapshot rehearsal on the supported host
  created a Python 3.10.12 virtual environment, installed the pinned runtime,
  started the host CLI, installed/listed Plugin 0.1.0 as enabled in an isolated
  Codex configuration, ran the anonymous quickstart, and passed the full suite
  in a refreshed allowlisted snapshot. Three independent ephemeral read-only
  Codex sessions then selected the correct Plugin-qualified Skill for one
  canonical prompt per route. The exact release-candidate commit replay is
  still `NOT_RUN`, so this is not final clean-clone release evidence.
- Real Cook/import/rollback, Unreal repair, CARLA server/runtime validation, HIL
  and cold-copy replay: `NOT_RUN`. UE4.27 target reopen/PIE/collision and a
  private matched Editor performance case study have run, but neither is a
  complete route.

## Evidence and residual risk

- Discovery, behavior baseline, migration matrix, and compatibility evidence:
  `development/local/analysis/` (local-only and intentionally ignored by Git).
- Implementation details: `IMPLEMENTATION_REPORT.md`.
- Release blockers and unimplemented adapters: `KNOWN_LIMITATIONS.md`.
- Publication scope and exclusions: `PUBLICATION_REDACTION_REPORT.md` and
  `PUBLICATION_ALLOWLIST.json`.
- The private historical Skill, 17 scripts and performance report were available
  and their recorded hashes were revalidated read-only during Phase A discovery.
- The supplied directory initially had no Git metadata. Local repository history
  now preserves the verified candidate baseline and subsequent structure changes.

The current tree is an inspect/plan/audit foundation, not a `v0.1.0-rc`.

## Historical evidence recovery addendum

Update: 2026-08-28 (Asia/Shanghai)

Read-only recovery found 19 route/status candidates created after the original
Phase A evidence set. They support the maintainer's statement that all three
routes were previously validated: a cross-route summary reports 49 passing
checks with no recorded failure or error, the Package CARLA records close an
archive-to-install consistency chain, and the UE4.27 records close a candidate
to second clean-project cold-copy content-consistency chain.

The records predate the current Verified Run contract. They do not provide a
current workspace, complete stage provenance, a frozen exact stack, a
rights-safe replay input, or current redaction/signoff evidence. Consequently
they remain historical characterization rather than current PASS evidence. A
later target-stage replay changes only its exact L3/L4 checks. The public-safe per-check binding and minimum
replay scope are recorded in
`development/shared/release-research/historical-evidence-binding-summary.md`.

## Exact stack lock addendum

Update: 2026-08-28 (Asia/Shanghai)

Read-only metadata and binary fingerprinting locked one exact stack for each
Primary Profile. The locks cover RoadRunner/exporter/plugin identity, Source and
Package CARLA 0.9.16, Source Unreal 4.26.2, vanilla Unreal 4.27.2, the matching
Package client/server pair and the Linux x86_64 host. See
`development/shared/release-research/three-primary-profile-stack-lock.md`.

This resolves version discovery only. External worktrees contain user changes,
the Package target lacks an accepted baseline, rights-safe inputs/projects are
not selected, and the current Toolkit snapshot is not frozen. The later private
UE4.27 target receipt is accepted only for its exact stage checks; it does not
remove the end-to-end or portability blockers.

## Execution-context adapter addendum

Update: 2026-08-28 (Asia/Shanghai)

The current candidate implements and tests the adapter-receipt schema, a
standard-library external context finalizer with Python 3.7-compatible syntax,
and the host `record-stage-evidence` command. Anonymous tests exercised Source
Unreal, UE4.27 Unreal, matching CARLA client/server and shell-build branches,
host validation of finalized receipts, boundary-integrity mismatch rejection,
plan/workspace/input
hashes, exact stage/context/evidence-type binding, public paths, private literal
scanning, atomic output, write-stage backup/rollback, all three routes' six-part
repair contract and guarded optimization apply contract.

The generic tests remain L2 evidence and do not execute route operations. On
2026-09-01 a separate authorized private collector exercised the real
`ue427-unreal-python` `SRC2UE427.TARGET_VALIDATE` path. The current finalizer
bound the draft to the sealed workspace/plan/input hashes and live UE4.27.2 API,
and the host recorder validated its structure and private-literal boundary.
Independent log review found 352 virtual-texture parameter errors in the first
candidate, so that PASS bundle was withdrawn. A sealed Unreal-API repair then
changed only the `virtual_texture_streaming` property on eight affected
textures. A fresh offscreen replay reported 605 assets, 9,438 static-mesh
actors, zero material/type/compiler errors, five Editor and five PIE collision
passes, 180 PIE frames and five fixed views. Paired quantitative and
non-automated visual review passed all 17 review assertions. The six-check
receipt was finalized against the live UE4.27.2 API and host-recorded into a
private sensitive-term-scanned stage candidate; project, map, configuration and
XODR hashes remained unchanged.

The same finalized private receipt was replayed through the stricter recorder
after it began requiring every stage check, a single boolean acceptance
observation per check, and no next-stage transition after failure. All six
required target checks passed and a new seven-file private bundle was written
without overwriting the earlier evidence.

A subsequent post-repair matched LOD replay captured 4,500 selected frames for
each state under one fixed five-view 640×372 Low offscreen protocol. Average FPS
improved 4.28%, mean frame time improved 4.10%, p95 improved 15.57% and GPU mean
time improved 15.83%, while draw calls increased 15.82%. Its 29-check postflight
is `REVIEW_REQUIRED`, not PASS, because median frame time improved only 0.56%
against the sealed automatic 3% threshold. The result is private one-host Editor
diagnostic evidence and does not extend the accepted route level.

This is an accepted current real target stage, not a complete L5 route run. The
write-stage migration/repair bindings, Source Unreal evidence, Package build and
runtime evidence, and rights-safe second-clean-project cold-copy remain
`NOT_RUN`.
