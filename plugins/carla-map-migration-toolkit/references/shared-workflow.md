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

The bundled host core currently implements inspect, plan, plan verification,
archive inspection, performance comparison, and pending validation reports. It
does not claim Editor/runtime work occurred. Missing environment evidence is
`NOT_RUN`, and unsafe prerequisites are `BLOCKED`.

Every command declares one context. Every route ends with a schema-valid
`map-handoff.json` that references existing stage artifacts; downstream routes
must revalidate it.
