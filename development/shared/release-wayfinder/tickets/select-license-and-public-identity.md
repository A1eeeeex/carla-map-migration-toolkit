---
title: Select the public license and accountable maintainer identity
label: wayfinder:grilling
mode: HITL
status: closed
assignee: codex
blocked_by: []
---

## Question

Which verified copyright holder, maintainer name, security contact and
open-source license will govern the public repository, Plugin metadata,
citations and release artifacts?

## Resolution

The individual named in `NOTICE.md` and `CITATION.cff` is the verified copyright
holder and accountable maintainer for the original public-candidate material.
The project uses the standard Apache License 2.0 (`Apache-2.0`). `LICENSE`
remains byte-for-byte standard license text; the legal name is not duplicated
outside the attribution and citation metadata.

The minimum-real-name policy keeps the legal name in attribution and citation
metadata. The stable public maintainer identity is the repository owner's
GitHub handle, `@A1eeeeex`; the Plugin name remains `CARLA Map Migration
Toolkit`. No private email, address or telephone number is published. Security
reports use GitHub private vulnerability reporting. Enabling and independently
checking that setting remains a separate `NOT_RUN` release task:
[`Enable and verify private vulnerability reporting`](enable-and-verify-private-vulnerability-reporting.md).

This decision does not authorize a push, public visibility change, tag or
GitHub Release. Background and official-source links are recorded in
[`individual-open-source-publication.md`](../../release-research/individual-open-source-publication.md).
