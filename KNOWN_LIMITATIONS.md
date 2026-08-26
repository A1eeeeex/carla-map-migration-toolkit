# Known limitations

## Release blockers

- No current-toolkit real end-to-end route replay has passed. The candidate is
  not `v0.1.0-rc`.
- No UE4.27 second clean-project cold-copy has run under the new contracts.
- No Package CARLA Cook, archive import, independent runtime validation, or
  rollback replay has run under the new contracts.
- No RoadRunner import can be compatibility-verified while the exact exporter
  and integration-plugin versions are unknown.
- No project-wide software license, maintainer identity, release repository, or
  security contact has been selected. The Plugin manifest therefore omits license
  and public URLs.
- No redistribution rights are established for the legacy Skill/scripts,
  historical evidence, or any private demo/map asset. They were not copied.

## Implementation gaps

- The bundled executable core is host-only. Source Unreal Python, UE4.27 Unreal
  Python, CARLA client, and shell-build adapters remain to be implemented and
  replayed.
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
  backup/rollback must be engine-aware and is not implemented.
- Static trigger expectations are checked for dataset coverage only. Model-level
  precision, recall, cross-route confusion, and safe-stop rates are `NOT_RUN`.
- The anonymous fixtures do not simulate real Unreal assets or CARLA behavior.
- Compatibility entries remain `experimental`; historical private claims cannot
  be promoted to current-toolkit PASS.

## Performance limits

- Historical UE4.27 Editor FPS is capped near 60, so FPS alone cannot prove the
  reported optimization.
- Historical Package baseline and candidate warmup/sample protocols differ and
  are not strictly comparable under the new contract.
- High-risk actor merge, ISM/HISM, texture, LOD, vegetation, and collision
  optimizations remain `REVIEW_REQUIRED` and have no current replay.

## Environment change observed during handoff

The private historical performance source was readable during discovery and its
SHA-256 was recorded in the source inventory. It was no longer available at its
discovery location during final recheck. The anonymous baseline remains, but the
source hash could not be revalidated at closeout.
