# Canonical schema location

Evidence schemas are maintained once under the Plugin `schemas/` directory.
This directory is an index rather than a duplicate source of truth. The Phase A
contracts currently include Claims Registry, Verified Run, structured check
evidence, private adapter receipts and redaction reports alongside route plan,
stage result, validation and handoff schemas. Adapter receipts are local inputs;
only their sanitized stage/check outputs belong in a public Verified Run.
