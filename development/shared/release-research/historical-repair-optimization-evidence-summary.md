# Historical repair and optimization evidence summary

Date: 2026-08-28

## Outcome

Read-only recovery confirms that the historical work covered more than the
three migration happy paths. Seventeen private scripts and the associated
records exercise material, reference, environment, collision, asset-migration,
package/runtime, cold-copy and performance domains. The private sources,
project-specific paths, thresholds, maps and binary artifacts are not copied
into this repository.

This evidence is useful for characterization and for minimizing replay. It is
not relabelled as a current Toolkit PASS because the old operations do not all
carry a sealed plan, explicit backup, rollback metadata, current context proof,
rights-safe input identity and public redaction envelope.

## Route coverage

| Route | Historical repair evidence | Historical optimization evidence | Smallest current action |
|---|---|---|---|
| RoadRunner to Source CARLA | Post-import material, external-reference, saved-state and Source audit signals are present. | Source content and non-regression audits are present. | Re-audit the current Source state; run a repair only for an observed finding. Capture a new comparable performance snapshot only if optimization is claimed. |
| Source CARLA to Package CARLA | Package archive/install consistency, runtime-domain checks and backup signals are present. | Source-side optimized-content audit and Package runtime samples are present. | Rebind archive/runtime facts; rerun the missing rollback contract. Package baseline/candidate timing must be resampled because the historical protocols differ. |
| Source CARLA to vanilla UE4.27 | Material/reference cleanup, environment replacement, collision persistence, target audit and cold-copy signals are present. | Content, transform, LOD, shadow, culling, Editor timing and protected-property audits are present. | Re-audit the already-repaired target rather than reapplying destructive changes. Bind cold-copy and repair receipts; recapture only evidence that cannot satisfy the current contract. |

## Repair contract binding

The legacy scripts collectively contain detect, apply and verification logic,
but the six phases were not consistently emitted as one machine-readable
record. Current repair evidence therefore requires affirmative observations for
all of:

```text
DETECT -> EVIDENCE -> PLAN -> APPLY -> VERIFY -> ROLLBACK
```

If the current audit is clean, no repair replay is required. A clean audit is
recorded as target validation; it must not be represented as a newly executed
repair. If a repair is required, the evidence adapter rejects PASS unless the
sealed write stage includes explicit apply mode, a hashed backup manifest,
rollback steps and the six observations above.

## Optimization binding

Historical content records show that optimization changed LOD/culling/shadow
configuration while preserving the recorded LOD0 proxy. Historical UE4.27
Editor sampling used matching declared conditions, but FPS was capped near 60.
Historical Package CARLA baseline and candidate sampling used different warm-up
and sample lengths, so that comparison cannot satisfy the current comparable-
conditions gate.

Current optimization apply evidence requires a passing functional baseline,
protected-property non-regression and rollback readiness. Performance
acceptance remains separate: identical hardware, resolution, quality, camera,
traffic, sensors, VSync/cap and sampling protocol are required, with frame time
reported alongside FPS.

## Release consequence

Historical repair and optimization work is confirmed and should be cited as
such. Formal route coverage still needs one sanitized current-contract Verified
Run for every Primary Profile. Optimization remains optional for the first
release candidate; if it is showcased, its comparison must independently pass
the current performance contract.
