# Evidence records

JSON is the source of truth. Markdown reports may render existing results but
must not recalculate or upgrade them.

- Canonical schemas live under
  [`plugins/carla-map-migration-toolkit/schemas/`](../plugins/carla-map-migration-toolkit/schemas/).
- Anonymous incomplete examples live under
  [`plugins/carla-map-migration-toolkit/examples/`](../plugins/carla-map-migration-toolkit/examples/).
- A real verified record belongs under `evidence/verified/<route>/<run-id>/`
  only after the route acceptance contract, required evidence level and
  redaction gate pass.

No current run is maintainer-verified. Historical private evidence cannot be
used as a verified record for the current toolkit.

A Source→UE4.27 `PASS` record must include the complete 15-check acceptance
contract, evidence for every required check, environment and target identity,
input/artifact hashes, stage results, protected-property evidence, redaction and
signoff. Public tests also resolve every verified compatibility/claim reference
to an existing matching record; a fabricated ID or path is rejected.

For a PASS record, input and artifact paths are repository-relative and confined
to that run's evidence directory. Required-check evidence must point to a
schema-valid PASS result for the check's catalog stage and execution context;
that stage check must cite a schema-valid `check-evidence` artifact bound to the
same run, route, stage and check ID. The check ID selects its required evidence
type, and PASS requires an explicit positive acceptance observation. Hashing
and structured parsing use the same byte snapshot. Empty, negative, manual-only
or generic supporting files cannot satisfy a higher-level required check.

The typed redaction report must bind the exact path and SHA-256 of every input
and non-report artifact, plus the scanner and a non-empty private sensitive-term
set fingerprint. The private terms themselves remain outside Git. Hashes alone
do not prove evidence meaning, and a count-only scan declaration is rejected.
The same private term set must be supplied out-of-band to cross-validation; a
PASS record fails closed when the set is absent, mismatched, or still appears in
the scanned UTF-8 evidence. The Verified Run and redaction-report envelopes are
also scanned directly; they are excluded only from the self-referential hash
manifest.
