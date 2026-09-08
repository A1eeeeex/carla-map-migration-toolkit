# Current status

Updated: 2026-09-08. Three route Skills plus guarded host helpers; guided Unreal/CARLA
operations, not an automatic importer or universally certified compatibility stack.

This is the starting point for evidence and compatibility questions. For usage,
start with [installation](installation.md) or the [capability list](capabilities.md).
Implementation gaps are collected in [known limitations](../KNOWN_LIMITATIONS.md);
historical reports and formal evidence rules are indexed under
[development references](../development/shared/README.md).

## Implemented capabilities

Inspect/plan, plan hashing, path/context guards, archive safety, named map/XODR
checks, Content-only audits, deterministic delivery manifests, performance
comparisons and context-bound evidence recording are implemented. Three thin
Skills load import/Cook, producer/receiver, material/daylight and staged
performance guidance as needed. See the [capability list](capabilities.md).

## Recorded real use versus a complete Verified Run

| Route | Existing observations | Important limit |
|---|---|---|
| RoadRunner → Source CARLA | Source Editor inspection and bounded CARLA 0.9.16 driving; 407 topology edges, 10,532 sampled waypoints and a 42.422 m driven path | Flat-road scope; elevated-road alignment unproven; handled renderer warnings recorded |
| Source CARLA → Package CARLA | Historical build/package/install consistency and runtime evidence, including the earlier cross-route summary | No fresh complete current-contract Package Verified Run |
| Source CARLA → UE4.27 | Second-clean-project structural inspection with 605 assets, later 180-frame PIE, sampled collision, five sunny views and Content-only archive/hash parity | Case-specific UE4.27.2 records, not a complete current-contract L5 Verified Run or a fresh post-extraction run on another machine |

The earlier blanket statements that Source runtime and second-project work had
not happened were stale. Preserve these later observations without relabelling
them as complete current-contract receipts. An initial capture marked visual
review NOT_RUN; a separate dated visual/log review subsequently passed. Keep
both records and their sequence.

The observed primary stacks remain RoadRunner R2025a / integration 1.4.4,
CARLA 0.9.16 / Source Unreal 4.26.2, matching Package CARLA 0.9.16 and vanilla
Unreal 4.27.2. No compatibility entry is changed to verified by this update.
Earlier details remain in [verification history](../VERIFICATION_STATUS.md)
and the [historical binding summary](../development/shared/release-research/historical-evidence-binding-summary.md).

## Latest lightweight checks

The public source commit `6222f0c` passed
[435 hosted tests](https://github.com/A1eeeeex/carla-map-migration-toolkit/actions/runs/34193021128)
in 11.26 seconds. The Unreal/CARLA job was skipped, not passed. An exact local
clone of that commit also passed runtime dependency installation, the anonymous
host demo and isolated Plugin installation. These are installation and host checks,
not new map migration evidence. The repository is now public; that does not by
itself mean a GitHub Release has been published.

The September 5 integration passed 435 host/fixture/structure tests, three
Skill validators and changed-file lint. A read-only audit of an existing
approximately 809 MB UE4.27.2 archive found 634 UE assets and the expected
Content-only layout. This is a different delivery revision from the 605-asset
case above, not an unexplained count change in one run.

Existing performance summaries were replayed over 16 counters, reporting both
improvement and regression. This does not establish a new matched-workload or
general speedup claim. The earlier matched LOD experiment remains
REVIEW_REQUIRED; headline improvements did not remove its tradeoffs.

Codex CLI 0.148.0 could no longer start the default model. A task-local
0.153.4 installation passed the 11-case changed-description/previous-failure
routing smoke. This is one description-based batch, not a complete installed-use
precision/recall study. No global Codex version or configuration was changed.

## Release boundary

The [release checklist](release-readiness.md) separates source distribution
readiness from strict v0.1.0-rc verification and actual GitHub publication.
There is no complete accepted current-toolkit Verified Run on all three Primary
Profiles; do not call this a certified RC.

Reuse existing evidence and test affected surfaces only. Documentation and
packaging changes do not require another map migration, engine launch, GPU
benchmark or complete history/log audit. New asset changes and new compatibility
claims still require their appropriate functional and portability gates.
