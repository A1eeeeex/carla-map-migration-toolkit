# Schema migrations

## Adapter-receipt 1.0.0

The new local-only receipt contract binds an external observation to a sealed
route plan, exact stage/context, versions, file hashes, actions, checks,
artifacts and rollback metadata. An optional `boundary` is added only by the
standard-library context finalizer and binds the receipt draft to that adapter's
hash and observed API context. Do not commit private receipt drafts, finalized
receipts, local paths or the sensitive-term set; publish only sanitized
stage/check artifacts after host validation.

## Phase A 1.0.0 to 1.1.0

Regenerate these artifacts; there is no compatibility adapter for stale plans
or evidence records:

- `route-plan`: `assets` now contains structured dependency action objects and
  the planner emits `schema_version: 1.1.0` from a single input snapshot.
- `verified-run`: every route has its full route-specific PASS contract. PASS
  artifacts use repository-relative paths and SHA-256 values; loaded public
  records are schema-checked and their referenced artifacts are rehashed.
- `compatibility-matrix`: every entry has `environment_sha256`; verified rows
  require it and must match the referenced run and visible stack fields.
- `claims-registry`: verified `supported_stacks` entries now contain `run_id`
  and `environment_sha256`.

This was the intermediate 1.1.0 contract. Do not relabel a 1.0.0 artifact:
regenerate it from the same inputs, then apply the current migration below.

## Phase A 1.1.0 to 1.2.0

- `route-plan`: verification rejects older plan versions, and
  `SRC2UE427.CLASSIFY_DEPS.assets` must satisfy the complete dependency-action
  shape.
- `verified-run`: route and artifact evidence are stricter. Package PASS now
  requires L5; artifact entries include a kind; stage results and redaction
  reports must validate against their schemas, match the run/route/check, hash
  correctly, and remain inside the run bundle.
- `claims-registry`: proof levels are L0–L5. `community-verified` remains the
  maturity status for an independently accepted reproduction.

Regenerate 1.1.0 route plans and Verified Run candidates. Do not relabel them.

## Route-plan 1.2.0 to 1.3.0 and redaction-report 1.0.0 to 1.1.0

- `route-plan`: executable dependency classes require non-empty source,
  strategy, action, verification, rollback and residual-risk fields. Unblocked
  plans are reclassified during verification so duplicate or incomplete action
  semantics cannot be hidden by resealing JSON.
- `redaction-report`: the scan declaration lists every covered repository-
  relative path and SHA-256, scanner identity, and the count plus SHA-256 of the
  private sensitive-term set. Verified Run validation requires that declaration
  to match every input and non-report artifact in the run bundle exactly; the
  same private set must be supplied out-of-band for the content scan.
- Verified Run cross-validation reads each input/artifact once for both hashing
  and JSON validation, and a required check must cite its catalog stage plus a
  hashed supporting or validation artifact.

Regenerate 1.2.0 route plans and 1.0.0 redaction reports from their original
inputs. Do not relabel old artifacts or copy private sensitive terms into Git.

## Verified-run 1.2.0 to 1.3.0 and route-plan 1.3.0 to 1.4.0

- `verified-run`: required stage checks may only cite typed `check-evidence`
  artifacts. Each artifact is schema-valid, non-empty, PASS, and bound to the
  same run, route, catalog stage and check ID with at least one observation.
- Verified Run, input, artifact and compatibility evidence paths must be
  normalized repository-relative POSIX paths. Absolute, parent-relative and
  backslash paths are rejected even when they resolve inside an allowed root.
- Redaction still binds the non-cyclic input/artifact manifest by path and hash;
  cross-validation additionally scans the Verified Run and redaction report
  bytes directly with the supplied private term set.
- `route-plan`: `steps` is non-empty, and verification requires the exact
  ordered stage catalog for the declared route before the plan may execute.

Regenerate old Verified Run candidates, check evidence and route plans. Do not
relabel records or synthesize observations from process exit codes.

## Check-evidence 1.0.0 to 1.1.0, Verified-run 1.3.0 to 1.4.0, and route-plan 1.4.0 to 1.5.0

- `check-evidence`: each route-required check ID now selects exactly one
  proof-capable evidence type: deterministic output, Editor audit, runtime
  measurement or portability replay. `manual-review` remains available only for
  non-contract evidence. A PASS record must contain exactly one positive
  `acceptance: true` observation and no negative acceptance; a FAIL record must
  contain exactly one negative acceptance observation and no positive
  acceptance. Other, non-acceptance observations may still contain false or
  zero-valued measurements.
- `verified-run`: the new version selects the stricter check-evidence contract;
  resealing hashes cannot make manual review or a negative acceptance
  observation satisfy an L3, L4 or L5 check.
- `route-plan`: verification binds every ordered step to the catalog's type,
  execution context and risk. Broad filesystem roots are rejected immediately,
  and workspace verification requires every read, write and backup path to
  exactly match the fingerprinted workspace's route path contract.

Regenerate all three artifact types from the original inputs. Do not relabel or
manually reseal stale records.
