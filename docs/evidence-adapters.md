# Execution-context evidence adapters

The adapters turn an operation's private receipt into schema-valid,
public-safe stage and check evidence. They support all three routes and the four
external contexts: Source Unreal, UE4.27 Unreal, CARLA client and shell build.
They do **not** execute migration, repair, optimization, build, import, runtime
or cold-copy operations.

## Two-step flow

1. The actual route operation writes a local `adapter-receipt` draft under the
   workspace artifact root. It declares the sealed plan hash, stage/context,
   exact versions, observations, hashes, changes and rollback metadata.
2. While the required external context is already running, load
   `scripts/context_receipt.py` and call `finalize_receipt(...)`, or invoke its
   CLI through that context's known launcher. This standard-library file uses
   Python 3.7-compatible syntax and verifies the live API boundary, workspace,
   sealed plan and input hashes.
3. Back in `host-cpython`, record the finalized receipt:

```bash
CMTK_EXECUTION_CONTEXT=host-cpython .venv/bin/python \
  plugins/carla-map-migration-toolkit/scripts/cmtk.py record-stage-evidence \
  --config <map-workspace.json> \
  --plan <route-plan.json> \
  --plan-sha256 <sealed-plan-sha256> \
  --receipt <finalized-private-receipt.json> \
  --output-dir <artifact-root/new-stage-evidence> \
  --evidence-prefix evidence/verified/<run-id>/stages/<stage> \
  --sensitive-terms <private-reviewed-literals.txt>
```

The host recorder rechecks the current receipt schema, installed boundary
adapter hash, plan/workspace/input hashes, exact route-stage-context binding,
required evidence type, positive/negative acceptance observation, local file
hashes, repository-relative public paths, private literals and generic
path/network/secret patterns. It writes a new directory atomically and refuses
to overwrite an existing bundle. A receipt must contain every required check
assigned to that stage. Each check status must agree with exactly one boolean
`acceptance` observation, and a failed stage exposes no next allowed stage.
Runtime measurements are emitted with sampled confidence rather than being
mislabelled deterministic.

The boundary hash provides deterministic integrity and adapter-version binding,
not a cryptographic identity attestation against a malicious runner. Verified
Run maintainer/reviewer signoff and independent reproduction remain separate
gates.

## Write-stage rules

A read-only stage must use `AUDIT`, declare no changes and mark rollback
`NOT_APPLICABLE`. A planned write stage must use `APPLY_SAFE` or `APPLY_PLAN`.
If its sealed plan requires backup, the receipt must include a hashed backup
manifest, rollback steps and `READY` or `VERIFIED` rollback status.

Repair PASS additionally requires affirmative `detect`, `evidence`, `plan`,
`apply`, `verify` and `rollback` observations. Optimization apply PASS requires
`functional_baseline`, `protected_properties_unchanged` and `rollback`.
Performance improvement is evaluated separately with the comparable-conditions
command and cannot be inferred from a successful optimization apply.

## Publication boundary

Receipt drafts, finalized receipts, sensitive-term files, local paths and raw
private artifacts stay outside Git. Only the sanitized `stage-result.json`,
typed check evidence and explicitly reviewed UTF-8 supporting artifacts may be
assembled into a public Verified Run. A finalized receipt is context evidence,
not a substitute for the underlying operation's measurements.
