# Known limitations

## Strict v0.1.0-rc gaps

See the [release checklist](docs/release-readiness.md) for the proposed
experimental distribution grade and its separate publication steps. Strict
Verified Run requirements remain unchanged; documentary reuse does not
satisfy missing current-contract stages.

- No current-toolkit real end-to-end route replay has passed. The candidate is
  not `v0.1.0-rc`.
- Second-project structural, PIE/visual and Content-only delivery records now
  exist, but they are not a complete current-contract UE4.27 Verified Run.
- No Package CARLA Cook, archive import, independent runtime validation, or
  rollback replay has run under the new contracts.
- The Primary RoadRunner stack is now locked to RoadRunner R2025a, its built-in
  Datasmith export identity and integration bundle 1.4.4, but no rights-safe
  current L4 replay has run.
- The repository is public and uses Apache-2.0. Repository visibility does not
  establish Release publication or activation of GitHub private vulnerability
  reporting; follow SECURITY.md and verify the private channel before disclosure.
- No redistribution rights are established for the legacy Skill/scripts,
  historical evidence, or any private demo/map asset. They were not copied.

## Implementation gaps

- Context receipt adapters now cover Source Unreal Python, UE4.27 Unreal Python,
  CARLA client and shell-build with L2 fixtures. They validate and record
  operation receipts; they do not implement route-specific migration, repair,
  Cook/import, runtime, PIE or cold-copy operations. One private collector has
  exercised a current real UE4.27 target-validation receipt path. Its first
  candidate was correctly withdrawn by strict material-log review; after a
  bounded eight-texture Unreal-API repair, a fresh six-check target stage passed
  and was host-recorded privately. No complete route, Source Unreal, CARLA
  client, shell-build or cold-copy receipt set exists yet.
- `map-handoff.json` has a schema and anonymous example, but no executable writer
  is exposed. A host-only writer cannot safely promote arbitrary JSON to L4/L5;
  future adapters must verify stage provenance, hashes, contexts, and artifacts.
- `apply-safe`, `apply-plan`, `guided`, and `resume` are defined workflow modes
  but are not exposed as executable CLI operations yet. This prevents accidental
  writes but means the current tree is an inspect/plan/audit foundation.
- Plans hash explicit RoadRunner/XODR inputs or, for downstream routes, the
  handoff, source asset inventory, dependency manifest, route manifest, and
  XODR. `verify-plan` rehashes these and the whole workspace. The manifests must
  still be produced from a trustworthy live adapter; plans do not capture a
  complete directory, Asset Registry, archive, free-space, or live target state.
- Backup helpers intentionally handle only explicit ordinary files. Unreal asset
  backup/rollback must be engine-aware and supplied by the actual operation
  adapter; the receipt recorder verifies the manifest but does not create it.
- Static coverage is not model proof. An 11-case description-based routing
  smoke passed on CLI 0.153.4; full current installed-use precision, recall
  and safe-stop rates are not established.
- The anonymous fixtures do not simulate real Unreal assets or CARLA behavior.
- Compatibility entries remain `experimental`; historical private claims cannot
  be promoted to current-toolkit PASS.

## Performance limits

- Historical UE4.27 Editor FPS was capped near 60, so those old FPS values alone
  cannot prove the reported optimization.
- Historical Package baseline and candidate warmup/sample protocols differ and
  are not strictly comparable under the new contract.
- A fresh private post-repair matched UE4.27 Stage-A LOD replay measured average
  FPS +4.28%, mean frame time -4.10%, p95 frame time -15.57%, GPU mean time
  -15.83% and primitives -75.06% at 640×372 Low, while draw calls increased
  15.82%. Median frame time improved only 0.56%, below the sealed automatic 3%
  acceptance threshold, so the result remains `REVIEW_REQUIRED`. This is a
  diagnostic one-host Editor result, not packaged-runtime or general-map
  performance proof.
- Actor merge, ISM/HISM, texture reduction, draw-distance, shadow and semantic
  object removal remain `REVIEW_REQUIRED`; none was applied in the measured
  Stage-A state.
- Historical repair and optimization evidence exists across all three routes,
  but it lacks one or more current plan/context/backup/rollback/redaction fields.
  The recovered evidence should drive targeted re-audit, not destructive
  reapplication of already-completed repairs.

## Real-use limitations

- A later Source handoff records a bounded flat-road driving probe, not
  all-road coverage. Two elevated visual roads did not match the supplied
  waypoint elevation; that scope remains unproven. Renderer warnings remain
  recorded rather than silently dismissed.
- A later UE4.27.2 case records 605 assets in a second clean project and
  subsequent PIE, collision, five sunny views and Content-only archive parity.
  Another machine opening the final extracted archive was not tested.
- The separately audited 634-asset delivery is another revision; do not combine
  it with the 605-asset case as though their maps or hashes were identical.
- Host delivery audits prove structure, not binary dependency closure;
  manifests and numeric deltas do not grant L3–L5 acceptance.

## Earlier Phase A environment boundary

The private historical Skill, 17 scripts and performance report were available
and revalidated read-only during Phase A. At that time no active workspace,
accepted Source handoff or authorized target was supplied, so the recovered
records remained characterization only.

Read-only recovery on 2026-08-28 subsequently confirmed historical validation
signals for all three routes, including Package archive/install consistency and
UE4.27 cold-copy content consistency. This narrows the replay scope but does not
remove the environment boundary: the recovered records still lack the current
workspace, stage provenance, rights-safe replay inputs and current
redaction/signoff evidence. Exact component stacks were subsequently locked,
but the observed dirty external environments remain unaccepted.

An authorized private target was later supplied for the 2026-09-01 UE4.27
stage replay. The initial material failure was repaired within an eight-texture
boundary and the fresh target stage passed reopen, inventory, strict material
log, sampled collision, PIE and fixed-view review. No private screenshot, log or
asset was published, and the sanitized stage candidate remains local. Later
authorized reimport/second-project work is now described above. Its records
remain case-specific and do not constitute a complete current-contract run or
grant redistribution rights to its map, screenshots or other private assets.
