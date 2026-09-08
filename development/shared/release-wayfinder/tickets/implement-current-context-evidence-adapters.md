---
title: Implement current execution-context evidence adapters
label: wayfinder:task
mode: AFK
status: closed
assignee: codex
blocked_by:
  - Bind historical validation to current-toolkit contracts
  - Freeze the three Primary Profile stacks
---

## Question

What is the smallest tested set of `source-unreal-python`,
`ue427-unreal-python`, `carla-client-python` and `shell-build` adapters needed to
emit current stage-bound evidence for the three minimum replay bundles while
preserving inspect/plan defaults, Unreal-safe asset operations, backups,
rollback metadata, stable reason codes and fail-closed context checks?

## Resolution

Implemented one local-only `adapter-receipt` contract, a standard-library
`context_receipt.py` finalizer with Python 3.7-compatible syntax, and the host
`record-stage-evidence` command. Together they cover `source-unreal-python`,
`ue427-unreal-python`, `carla-client-python` and `shell-build`, bind receipts to
the sealed workspace/plan/input hashes and exact route stage, probe the live
API boundary or shell receipt, validate exact versions/platform, evidence type,
acceptance observation, artifacts, private literals, public paths and atomic
no-clobber output. The recorder requires every check assigned to the stage,
requires one matching boolean acceptance observation per PASS/FAIL, and exposes
no next-stage transition after a failed check.

Planned write stages require explicit apply mode, hashed backup manifest and
rollback metadata. All three routes expose optional repair and optimization
stage evidence: repair PASS requires DETECT/EVIDENCE/PLAN/APPLY/VERIFY/ROLLBACK;
optimization apply PASS requires a functional baseline, protected-property
non-regression and rollback. The RoadRunner material/reference checks were
corrected from the CARLA-client target stage to Source Unreal post-import audit.

Anonymous L2 tests cover all four context branches, host recording of finalized
receipts, tamper/integrity failures, the three routes' repair and optimization
contracts and fail-closed path/hash/context/redaction behavior. The adapters do
not execute route operations; real L3–L5 receipts remain `NOT_RUN` until
rights-safe projects/inputs and accepted external environments are supplied.

## Post-resolution evidence

On 2026-09-01 an authorized private UE4.27.2 target collector exercised the
current finalizer and host recorder. Strict review withdrew its first candidate
after finding 352 material errors the collector had not modeled. The collector
was strengthened with an explicit log gate; a sealed Unreal-API repair changed
only eight affected texture properties and retained rollback metadata. A fresh
offscreen replay then passed all six target-stage checks, five fixed-view review
cases and the live UE4.27.2 boundary, and the host recorder generated a private
sensitive-term-scanned stage candidate. No map identity, path, screenshot, log
or binary was published. This is accepted target-stage evidence, not a complete
route Verified Run or an L5 claim. The same finalized six-check receipt later
passed the stricter recorder and produced a new local bundle without overwriting
the original evidence.
