# Route-scoped map performance operations

Read this only for optimization of a map on one of the three supported routes.
It supplements the [performance contract](performance-protocol.md), not a
general engine-tuning or vehicle-controller skill. Bundled commands compare
evidence; they do not automatically profile or modify Unreal assets.

## Measure a useful baseline

Start after functional validation. Record the exact project/map revision,
engine/build, hardware and profile. Pin resolution, scalability, camera route,
route speed and duration, traffic, sensors, warmup and repeat count. Bind a
moving driving/view route and speed into the camera-profile hash; a static
beauty shot cannot substitute for a driving workload. Separate cold-start and
warmed runs. Record VSync, FPS cap, streaming/shader progress and sample count.

Check available counters in the installed engine before selecting profiling
commands (`stat unit`, `stat RHI`, `stat GPU`, CSV profiling where supported).
Collect Frame, Game/Render/RHI thread time, GPU time, draw calls, primitives,
RAM/VRAM and available BasePass, PrePass, Shadow and GPUSceneUpdate timings.
Preserve units, mean/median/p95/p99 and aligned sample windows; counter names
and availability depend on engine/build. A capped frame time can conceal a
GPU reduction, but lower GPU time alone does not prove faster driving.

Reuse sufficiently matched existing samples first. Before a new heavy run,
check free VRAM and wait for resources; never repeatedly launch editors or
servers into an exhausted GPU. Plan a bounded sample, not continuous polling
or a full migration replay after each tuning change.

## Diagnose before choosing a change

| Dominant cost | Candidate investigation | Preservation / approval boundary |
|---|---|---|
| Game thread or update cost | Tick, actor/component counts, collision queries | Preserve traffic, triggers, routes and simulation behavior |
| Draw/RHI or draw calls | Repeated decorative meshes, material sections | Instancing/merging needs review; preserve transform, semantics and material slots |
| GPU BasePass / primitives | Additional LODs, decorative visibility distances | Preserve LOD0 and road geometry; avoid visible popping |
| Shadow cost | Nonessential decorative shadow casters and distance | Review visual tradeoffs; do not blanket-disable scene shadows |
| GPUSceneUpdate | Primitive updates, visibility churn, instance changes | Check Game/Draw/RHI regressions, not just GPU totals |
| Memory/streaming | Texture residency, duplicates, material dependencies | Downsampling or virtual-texture changes require review and visual validation |
| Collision cost | Query settings and declared collision profile | No blanket collision removal; drivable and required obstacle collision must remain |

Each candidate records scan/detect, evidence, plan, apply, verify and rollback
metadata. Preserve LOD0, material slots, transforms, road geometry, XODR and
drivable collision. Roads, markings, traffic facilities, Route Planners,
triggers and independently semantic objects are not merge/prune candidates by
default. Actor merge, ISM/HISM, auto-LOD, culling/pruning, texture downsampling
and collision changes are `REVIEW_REQUIRED`, not automatic fixes. Material
deduplication must respect referencers and actual equivalence, not filenames.

Keep experiments separate from the delivery candidate. Pick one change class,
check the affected function/view and sample the same route. Reject or roll back
bad candidates. Do one consolidated final functional/performance/cold-copy
check for the selected result where that route requires it. Stop when the
agreed target is met, gains are within run variance, or the remaining tradeoff
needs user approval; do not claim a map is "fully optimized".

## Compare existing profiling summaries

From the installed repository root, in `host-cpython`:

```bash
CMTK_EXECUTION_CONTEXT=host-cpython .venv/bin/python plugins/carla-map-migration-toolkit/scripts/cmtk.py compare-metrics --baseline <baseline.json> --candidate <candidate.json> --allowed-root <input-root> --allowed-root <report-root> --stat mean --output <report-root>/metric-deltas.json
```

Input is a metric-name dictionary, either directly or under `metrics` when
metadata is present. Each value is a number or an object such as
`{"mean": 4.0, "median": 3.9, "p95": 5.1}`. Select `mean`, `median`, `p95`,
`p99` or `max`. By default it compares the union of counters; repeated
`--metric` narrows the selection. FPS names are higher-is-better; use repeated
`--higher-is-better` for other such metrics. Other counters default to lower-
is-better; select only metrics for which that interpretation makes sense.

The result lists improvements, regressions, missing and invalid values. Zero
baselines have no percentage rather than a fabricated 100% gain. Booleans,
negative and nonfinite values are invalid. Output is diagnostic `WARN` (or
`FAIL` on invalid/empty data), with `optimization_acceptance: NOT_RUN`, even
when all counters improve. Arbitrary matching metadata is not comparability
proof, and a regression may represent an explicitly accepted tradeoff.

For acceptance use `compare-performance` with the existing snapshot contract:
complete matching conditions, median/p95 frame time and protected-property
hashes. Primary frame-time or preservation failures remain `FAIL`. Optional
counter regressions or missing optional counters produce `WARN`; invalid
optional values fail. A faster Frame metric must not hide slower GameThread,
GPUSceneUpdate or other reported counters. Numeric gates supplement, not
replace, real route-specific functional validation.
