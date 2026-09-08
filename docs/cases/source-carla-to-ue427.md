# Source CARLA to UE4.27 migration case

[中文版本](source-carla-to-ue427.zh-CN.md)

A custom road scene was migrated into a standalone UE4.27 project, repaired for
sky and material issues, and used to evaluate an LOD change that was ultimately
rolled back. This is a historical engineering case; the map is not distributed.

## Scope and results

- **Route:** Source CARLA → vanilla UE4.27.2, with Content delivery to an independent project.
- **Migration:** clean-project structural inspection recorded 605 assets, including
  241 static mesh assets, with no missing internal dependencies, external-project
  dependencies or unloadable assets.
- **Repairs:** later records include project reopening, material checks, PIE,
  sampled road collision checks and fixed-view visual inspection after the sky repair.
- **Performance:** the LOD candidate did not deliver an accepted end-to-end improvement
  and was rejected and rolled back.

## Migration steps

1. **Establish a baseline.** Preserve the source project and staging copy; record
   asset inventories, dependencies and hashes.
2. **Migrate dependencies.** Use the Editor's Migrate workflow to transfer the map
   and its dependencies through a staging project into the target.
3. **Resolve target differences.** Address environment, material and reference
   issues in UE4.27, save the changes, then inspect the target again.
4. **Check independent delivery.** Migrate into a clean UE4.27 project, inspect its
   dependencies, reopen it and run checks. Later repairs receive separate validation.

Codex organizes the route, inspection and plan. Host scripts check packages,
manifests and metrics. Migrate, asset property changes, saving and PIE execute
inside Unreal; a host CLI command does not perform those Editor operations.

## Sky and material repairs

| Before repairs | After repairs |
|---|---|
| ![Earlier road scene with a dark red sky](../assets/showcase/before.png) | ![Final capture of the same road under a sunny sky](../assets/showcase/after.png) |

*Approximately matched viewpoints from the earlier baseline and final capture.
Several repairs separate the views; this is not a single-parameter experiment.
Screenshot pixels are unchanged.*

| Finding | Bounded repair |
|---|---|
| Virtual-texture settings on 8 textures did not match their material parameters | Check referencers, disable virtual texture streaming on those textures and recheck materials |
| Incorrect sky scattering settings | Adjust Rayleigh and Mie scattering scales on the native SkyAtmosphere |
| Fog inscattering was too dark | Adjust native fog inscattering color alongside the sky settings |

Writes were limited to the map and texture packages allowed by the plan, with
backup and rollback records retained. A fresh UE4.27.2 process then reopened the
project for material, PIE, sampled road collision and fixed-view visual checks.
Saving the changes alone was not treated as repair acceptance.

## LOD experiment and rollback

After a passing functional baseline, an LOD candidate was measured under matched conditions:

| Metric | Baseline | LOD candidate |
|---|---:|---:|
| Average FPS | 113.40 | 112.81 |
| Mean frame time | 8.818 ms | 8.864 ms |
| P95 frame time | 8.729 ms | 8.713 ms |

The candidate reduced drawn primitives by about 76.79%, but increased draw calls
by about 16.22%. Mean frame time did not improve; P95 improved by only about 0.18%.

**Decision: roll back the LOD candidate.** It did not meet the predeclared 3%
useful-gain threshold. Records confirm rollback and revalidation. Higher-risk
shadow or draw-distance changes were not pursued.

Measurement conditions: Intel i5-14400F, RTX 4060 Ti 8 GB, Ubuntu 22.04.5,
UE4.27.2; 640×372, Low quality, VSync off, no FPS cap. Five fixed views were
sampled three times each, with 300 frames per sample and 240 warm-up frames:
4,500 selected frames per baseline/candidate. The protocol records matching
camera, traffic and sensor configurations.

The 1600×900 visual captures above are not the performance sampling configuration.
This earlier LOD experiment also does not measure the later sunny scene's performance.

## Evidence and limits

This case summarizes records from 2026-09-01: migration receipts, cold-copy
structural inspection, sky/material repair and runtime/visual checks, LOD
comparison and rollback decisions. Raw records contain private paths and asset
identifiers and are not distributed with the case.

- Historical observations cover Editor, Runtime/PIE and cold-copy structural
  checks. They are not a new acceptance run or complete current-version
  verification of all three routes.
- Screenshots show appearance, not proof of runtime behavior, performance or portability.
- Only authorized anonymous screenshots and aggregate metrics are shared.
  Map, texture, XODR and project assets remain private.
- A future downloadable, reproducible public Golden Map is separate from this case
  and will not distribute this map's assets.
