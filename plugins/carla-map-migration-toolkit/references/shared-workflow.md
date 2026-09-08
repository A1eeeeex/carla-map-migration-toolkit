# Shared workflow

All three routes use:

```text
DISCOVER → PREFLIGHT → BASELINE → PLAN → MIGRATE → REPAIR
→ FUNCTIONAL VALIDATION → OPTIMIZE (optional) → TARGET VALIDATION → HANDOFF
```

Start in `inspect` or `plan`. `apply-safe` requires a sealed plan, input and
environment revalidation, an explicit backup, and only low-risk actions.
`apply-plan` additionally requires the reviewed plan hash. `guided` pauses at
Editor checkpoints and audits actual results afterward. `validate` is read-only.

The bundled core implements inspect, plan, plan verification, archive
inspection, performance comparison, pending validation reports and guarded
recording of receipts finalized in `source-unreal-python`,
`ue427-unreal-python`, `carla-client-python` or `shell-build`. Receipt recording
does not execute Editor/runtime work and cannot prove work for which no
underlying context observation exists. Missing evidence is `NOT_RUN`, and
unsafe prerequisites are `BLOCKED`.

For bounded delivery work it also provides `map-package-audit`, `content-audit`,
`delivery-manifest` and `compare-metrics`. These run in `host-cpython`, do not
require a live Editor and never mutate map assets. Inputs and optional new
reports must be inside explicit allowed roots; reports cannot overwrite inputs
or existing files. Runtime/cold-copy and optimization acceptance remain
`NOT_RUN` in these diagnostics. See [Content delivery](ue427-content-delivery.md)
and [map performance operations](map-performance-operations.md).

Repair receipts can PASS only with DETECT/EVIDENCE/PLAN/APPLY/VERIFY/ROLLBACK
observations plus the planned write mode, backup manifest and rollback steps.
Optimization apply receipts additionally require a functional baseline,
protected-property non-regression and rollback readiness; performance
improvement is decided separately by the comparable-conditions contract.

Every command declares one context. Every route ends with a schema-valid
`map-handoff.json` that references existing stage artifacts; downstream routes
must revalidate it.
