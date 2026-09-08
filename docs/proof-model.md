# Proof model

| Level | Evidence | What it can prove |
|---|---|---|
| L0 | Plugin/Skill/schema/link validation | Structure only |
| L1 | Deterministic path/hash/plan/status/redaction tests | Pure host logic |
| L2 | Anonymous Source/target/fault fixtures | Fixture workflow behavior |
| L3 | Real Source CARLA or UE4.27 Editor action/audit | Editor compatibility on the recorded stack |
| L4 | CARLA runtime or UE4.27 PIE smoke | Runtime behavior on the recorded stack |
| L5 | Independent clean target or second-project cold-copy | Portability on the recorded stack |

JSON artifacts are the source of truth. Reports render existing statuses and do
not recalculate them. A compatibility row with `maintainer-verified` or
`community-verified` must cite both a `verified_run_id` and its evidence path.
`community-verified` is a maturity status for an accepted independent replay;
its proof level remains within L0–L5 and must meet the same route minimum.
The L1 publication tests load every public Verified Run and cross-check those
references against route, owner, toolkit version, claim ID, catalog stage,
proof-capable evidence type, positive structured acceptance, underlying hashes,
redaction coverage and repository-relative evidence path; schema-valid strings
alone do not establish traceability.

For required checks: any `FAIL → FAIL`, then `BLOCKED → BLOCKED`; `NOT_RUN` or
`NOT_APPLICABLE → INCOMPLETE`; only all required `PASS` can produce `PASS`. A
lower evidence level cannot be used to make a higher-level compatibility claim.
