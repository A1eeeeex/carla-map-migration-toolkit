# Map performance became worse after optimization

## Symptoms

FPS improves in one view but p95 frame time, another thread or the moving workload regresses; or a lower GPU time does not improve a capped run.

## What usually needs checking

Match hardware, engine, resolution, quality, camera route, traffic, sensors, warmup, VSync and FPS cap. Compare units and sample windows; preserve LOD0, material slots, transforms, road geometry, XODR, collision and semantics.

## Toolkit diagnosis

From the installed clone in host-cpython; replace every angle-bracket value
with your own permitted local input before running:

```bash
CMTK_EXECUTION_CONTEXT=host-cpython .venv/bin/python plugins/carla-map-migration-toolkit/scripts/cmtk.py compare-metrics --baseline <baseline.json> --candidate <candidate.json> --allowed-root <input-root> --stat p95
CMTK_EXECUTION_CONTEXT=host-cpython .venv/bin/python plugins/carla-map-migration-toolkit/scripts/cmtk.py compare-performance --baseline <baseline-snapshot.json> --candidate <candidate-snapshot.json> --allowed-root <input-root>
```

compare-metrics accepts numeric metric dictionaries or per-stat summaries and reports diagnostic WARN even when all improve; optimization_acceptance stays NOT_RUN. compare-performance needs the full existing snapshot contract. PERF-CONDITIONS-NOT-COMPARABLE rejects mismatched conditions; PERF-P95-REGRESSION fails the tail gate; PERF-SECONDARY-REGRESSION warns about optional counters.

## Manual / Editor checkpoint

Use the existing performance snapshot example, not arbitrary metadata as comparability proof. In the correct engine context inspect the dominant thread/GPU/streaming cost; test one reviewed change at a time and wait for free VRAM before launching. Reuse matching samples when possible.

## Validation

Recheck affected function/views, then the same bounded workload. Reject or roll back candidates violating protection or primary gates. Review secondary tradeoffs explicitly; a diagnostic number alone is not acceptance.

## Evidence to keep

Both raw local samples and public-safe summaries, fixed conditions, metric units, mean/median/p95/p99, protected-property hashes, candidate diff and rollback decision.

## What this guide does NOT prove

The CLI does not collect engine counters or optimize assets. It does not promise universal speedups or simulation equivalence after mesh, LOD, texture or collision changes.

Based on the repository's [operation reference](../../plugins/carla-map-migration-toolkit/references/map-performance-operations.md),
[reason codes](../../plugins/carla-map-migration-toolkit/references/reason-codes.md)
and existing host/fixture checks. [Back to cookbook](README.md).
