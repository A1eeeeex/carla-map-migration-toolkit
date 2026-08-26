# Repair contract

Every repair module has six evidence-bearing phases:

```text
DETECT → EVIDENCE → PLAN → APPLY → VERIFY → ROLLBACK
```

Record the detector inputs, reason code, confidence, expected/actual changes,
risk, backup manifest, acceptable-change allowlist, verification evidence,
residual risk, and rollback operation. Never return success immediately after an
apply operation. Repeat the original failing path in the target environment.

Material, reference, redirector, collision, world, traffic, Cook, asset
replacement, and optimization changes that can alter semantics are
`REVIEW_REQUIRED`. Editor-only actions are `EDITOR_CHECKPOINT` and remain
`NOT_RUN` until a deterministic post-action audit observes the result.
