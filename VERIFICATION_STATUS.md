# Verification status

Date: 2026-08-26 (Asia/Shanghai)

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
- RoadRunner/exporter version: unknown.

These are environment observations, not compatibility PASS claims.

## Evidence by level

| Level | Status | Evidence |
|---|---|---|
| L0 structure | PASS | Canonical Plugin validator and all three canonical Skill validators passed. Six schemas, examples, profiles, manifests, and links are covered by tests. |
| L1 pure logic | PASS | The full host-side test suite and Ruff checks passed; exact closeout commands and counts are recorded below. |
| L2 anonymous fixtures | PASS | Ten text-only fixture families cover route, archive, performance, schema, safety, and CLI behavior without real map or engine assets. |
| L3 Editor | NOT_RUN | No current-toolkit Source CARLA or UE4.27 Editor adapter/replay was run. |
| L4 runtime | NOT_RUN | No current-toolkit Package CARLA/CARLA Python API/PIE replay was run. |
| L5 portability | NOT_RUN | No second clean-project UE4.27 cold-copy replay was run. |

## Closeout commands

The following commands ran against the final implementation sources:

```text
python3 .../plugin-creator/scripts/validate_plugin.py plugins/carla-map-migration-toolkit
  PASS — Plugin validation passed
python3 .../skill-creator/scripts/quick_validate.py <each of three Skill directories>
  PASS — Skill is valid! (3/3)
python3 -m ruff check --no-cache plugins/carla-map-migration-toolkit/scripts/cmtk tests
  PASS — All checks passed!
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider
  PASS — 220 passed in 1.25s
```

The full pytest result includes the exact-file publication allowlist scan, all
six schema/example checks, 73 static trigger cases, 12 behavior cases, CLI
integration tests, and unit tests.

Two intermediate full-suite runs reported `218 passed, 2 failed`: the new
publication gate correctly detected generated `.pyc` files. The first run placed
official validators before pytest; the second exposed one CLI subprocess test
that replaced rather than inherited the bytecode-suppression environment. The
test harness now preserves the environment, generated caches were removed, and
the final clean rerun above passed. No product failure was hidden or reclassified.

## Additional NOT_RUN items

- Model-based Skill trigger precision/recall/confusion evaluation: `NOT_RUN`.
  Static dataset shape and expected-route assertions run at L1 only.
- Hosted GitHub Actions L0–L2 execution: PASS for `main` commit `9743ab3`:
  `https://github.com/A1eeeeex/carla-map-migration-toolkit/actions/runs/32941292193`.
- Clean-clone installation: `NOT_RUN`; repository initialization does not prove
  installation in a separate environment.
- Real Cook/import/rollback, Unreal repair, CARLA runtime validation, PIE, HIL,
  and performance replay: `NOT_RUN`.

## Evidence and residual risk

- Discovery, behavior baseline, migration matrix, and compatibility evidence:
  `development/local/analysis/` (local-only and intentionally ignored by Git).
- Implementation details: `IMPLEMENTATION_REPORT.md`.
- Release blockers and unimplemented adapters: `KNOWN_LIMITATIONS.md`.
- Publication scope and exclusions: `PUBLICATION_REDACTION_REPORT.md` and
  `PUBLICATION_ALLOWLIST.json`.
- The private historical performance source was available during discovery but
  unavailable at closeout, so its recorded discovery hash was not revalidated.
- The supplied directory initially had no Git metadata. Local repository history
  now preserves the verified candidate baseline and subsequent structure changes.

The current tree is an inspect/plan/audit foundation, not a `v0.1.0-rc`.
