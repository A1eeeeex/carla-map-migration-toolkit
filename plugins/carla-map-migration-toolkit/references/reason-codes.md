# Reason codes

`reason-codes.json` is the machine-readable catalog. A code is evidence of a
specific gate or observation, not proof that an entire route passed. Codes with
`no_auto_repair` stop automatic work; `checkpoint` requires an observed Editor
action followed by audit; `review_required` requires an approved plan.

Do not turn an unknown condition into `PASS`. Use `NOT_RUN` when a check was not
executed and `BLOCKED` when a prerequisite makes execution unsafe.

For Source CARLA → UE4.27 dependency planning:

- `UE427-DEPENDENCY-MANIFEST-INVALID` means the Source inventory contract cannot
  be read as a dependency array;
- `UE427-DEPENDENCY-MANIFEST-EMPTY` means the manifest provides no dependency
  facts and cannot prove that classification is complete;
- `UE427-DEPENDENCY-UNKNOWN` means classification or required action metadata is
  incomplete;
- `UE427-DEPENDENCY-BLOCKED` means a known dependency has no supported migration
  strategy;
- `UE427-REPLACEMENT-UNDEFINED` means a replaceable dependency has no approved
  target strategy.

`EVIDENCE-REFERENCE-INVALID` blocks a Verified compatibility or claim record
when its referenced Verified Run is absent or does not match the route, owner,
toolkit version, claim, or declared evidence path.

`EVIDENCE-RECORD-INVALID` blocks a loaded Verified Run that fails its versioned
schema, refers to unmanifested evidence, has missing/mismatched artifact hashes,
or lacks a signoff hash represented by its artifact manifest.
