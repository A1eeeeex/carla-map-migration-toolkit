# Development reference index

These documents are for maintainers and readers investigating implementation or
evidence details. They are not prerequisites for using the Plugin. Start with
[installation](../../docs/installation.md), [capabilities](../../docs/capabilities.md)
and [current evidence](../../docs/current-status.md) for the user-facing view.

## Design and verification rules

- [Architecture decision](../../docs/architecture/decisions/ADR-001-route-skills.md)
- [Acceptance contracts](../../docs/acceptance-contracts.md) and [proof model](../../docs/proof-model.md)
- [Claims](../../docs/claims.md), [non-claims](../../docs/non-claims.md) and [support definitions](../../docs/support-status.md)
- [Claim-to-test mapping](../../docs/claim-test-traceability.md)
- [Evidence adapters](../../docs/evidence-adapters.md) and [schema migrations](../../docs/schema-migrations.md)

## Recorded real use

- [Historical route evidence](release-research/historical-evidence-binding-summary.md)
- [Repair and optimization evidence](release-research/historical-repair-optimization-evidence-summary.md)
- [Observed version stacks](release-research/three-primary-profile-stack-lock.md)
- [Verification history](../../VERIFICATION_STATUS.md)

These records describe their dated scope. They do not override the current
status page or turn incomplete current-contract evidence into a verified route.

## Development and release history

- [Implementation report](../../IMPLEMENTATION_REPORT.md) and [Phase A closeout](../../PHASE_A_CLOSEOUT.md)
- [Release preparation checklist](../../docs/release-readiness.md) and [planning map](release-wayfinder/map.md)
- [Publication review report](../../PUBLICATION_REDACTION_REPORT.md) and [audit tooling](release_tools/README.md)
- [Installation research](release-research/codex-plugin-installation.md)
- [Individual publication research](release-research/individual-open-source-publication.md)

Historical reports, research and task tickets may describe earlier states. They
are retained for traceability, not a second current-status source. Their paths
remain stable so existing references continue to work.

## Adding material

Keep publication-safe proposals and reviews here; keep original inputs and private
working records under the Git-ignored local directory described in the
[development guide](../README.md). New public files must be explicitly added to
`PUBLICATION_ALLOWLIST.json` and pass the publication allowlist and redaction tests.
