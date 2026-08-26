# Reason codes

`reason-codes.json` is the machine-readable catalog. A code is evidence of a
specific gate or observation, not proof that an entire route passed. Codes with
`no_auto_repair` stop automatic work; `checkpoint` requires an observed Editor
action followed by audit; `review_required` requires an approved plan.

Do not turn an unknown condition into `PASS`. Use `NOT_RUN` when a check was not
executed and `BLOCKED` when a prerequisite makes execution unsafe.
