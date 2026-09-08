---
title: Complete the private-literal and full-history publication audit
label: wayfinder:task
mode: AFK
status: closed
assignee: codex
blocked_by: []
---

## Question

Can the private source register produce a non-published prohibited-literal set
that proves the current tree, all reachable Git blobs, and any private GitHub
Actions logs or artifacts contain no customer, project, map, host or credential
material before visibility changes?

## Resolution

No. The private source register contains 19 redacted logical URIs and hashes,
but none of the original source paths is available through the register, so it
cannot reconstruct or prove an authoritative private literal set.

A fail-closed `host-cpython` audit gate now scans tracked paths and contents,
all locally reachable Git objects and refs, and a caller-supplied unpacked
external export. It never echoes matching literals. Empty literal sets, missing
or empty exports, unsafe entries and dirty worktrees are blockers rather than
passes.

The real repository audit remains `NOT_RUN`: it requires the newly split
owner-approved literal-set task, a complete authenticated GitHub Actions export
and an authenticated audit of GitHub-only refs. No visibility change is
authorized by this resolution.
