# Historical validation binding summary

Date: 2026-08-28

## Outcome

Recovered records support the maintainer's statement that all three migration
routes were previously validated. The recovery found a passing cross-route
summary with 49 checks, a Package CARLA archive/install consistency chain, and
a vanilla UE4.27 cold-copy content-consistency chain.

This is meaningful historical evidence, but it is not a current-toolkit
Verified Run. The old records do not carry the complete current workspace,
stage provenance, exact accepted stack, rights-safe input, redaction and
signoff contract. Therefore all 41 current required checks remain `NOT_RUN` and
must receive current evidence. Historical results are used to avoid blind or
duplicative replay and to define the smallest credible stage bundle.

## Binding method

- `DIRECT`: the old record explicitly supports the substance of the current
  check.
- `PARTIAL`: the old record supports part of the check but lacks one or more
  current-contract assertions.
- `NO_MATCH`: no recovered record safely supports the current check.

Across the three Primary Profiles, the 41 required checks bind as 15 direct,
20 partial and 6 no-match. These labels describe historical relevance only;
none is a current PASS.

## RoadRunner to Source CARLA

Primary Profile: `roadrunner-datasmith`. Required evidence level: L4.

- Direct (4): `source_target_identified`, `editor_reopen`,
  `required_materials_valid`, `external_refs_resolved`.
- Partial (6): `input_profile_identified`, `environment_versions_recorded`,
  `import_committed_saved`, `opendrive_map_match`, `spawn_points_profile`,
  `vehicle_spawn_collision`.
- No match (2): `topology_junction_core`, `source_handoff_complete`.

Minimum current replay: host discovery, environment preflight, export
validation and handoff; real Source CARLA baseline, target preparation, import
checkpoint, editor reopen audit, functional validation and target validation.
Run repair only if the audit requires it. Optimization is outside the release
gate unless explicitly requested.

## Source CARLA to Package CARLA

Primary Profile: `content-package`. Required evidence level: L5.

- Direct (6): `package_config_valid`, `package_artifact_hashed`,
  `archive_safety_passed`, `target_backup_complete`, `road_collision_smoke`,
  `dynamic_smoke`.
- Partial (7): `build_target_os_match`, `cook_dependencies_complete`,
  `package_registry_visible`, `load_world_stable`, `source_visual_parity`,
  `opendrive_spawn_expected`, `rollback_ready`.
- No match (1): `source_handoff_passed`.

Minimum current replay: host handoff read, output selection, preflight,
baseline, package configuration audit, archive audit and handoff; real cook
dependency audit, build, target backup, import and CARLA runtime validation.
Run repair only if required. Optimization is outside the release gate unless
explicitly requested.

## Source CARLA to vanilla UE4.27

Primary Profile: `standalone-map`. Required evidence level: L5.

- Direct (5): `source_asset_inventory_complete`,
  `target_engine_version_recorded`, `required_assets_present`,
  `missing_assets_zero`, `road_collision_smoke`.
- Partial (7): `unreal_safe_migration`, `required_materials_valid`,
  `disallowed_carla_refs_zero`, `runtime_objects_have_strategy`,
  `target_reopen`, `pie_smoke`, `second_clean_project_cold_copy`.
- No match (3): `dependency_classification_complete`,
  `world_settings_environment_lighting`, `ue427_handoff_complete`.

Minimum current replay: host handoff read, preflight, dependency classification
and handoff; real Source/UE4.27 baseline, clean target creation, Unreal-safe
migration, required repairs/replacements/reference cleanup, target reopen and
PIE validation, then a second clean-project cold copy. Optimization and HIL are
not part of the `standalone-map` release gate.

## Release consequence

The project has credible evidence that the three routes worked before; it does
not need a blind full rediscovery. Formal publication still requires one
current, sanitized Verified Run for each Primary Profile. Exact stacks are
frozen and the evidence adapters now exist; rights-safe replay inputs/projects,
route-specific operation receipts and accepted external environments are still
required before those runs.

Historical repair and optimization coverage is summarized separately in the
[public-safe repair/optimization evidence summary](historical-repair-optimization-evidence-summary.md).
It supports targeted re-audit instead of destructive reapplication: an already
repaired map should not be modified merely to recreate an old operation.
