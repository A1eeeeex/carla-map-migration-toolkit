---
title: Export and audit the private GitHub Actions history
label: wayfinder:task
mode: AFK
status: open
assignee: codex
blocked_by:
  - Supply and approve the authoritative private literal set
---

## Question

Can an authenticated, complete and safely unpacked export of every private
workflow log and artifact in scope pass the publication audit against the
approved private literal set without publishing the export or its contents?

## Progress

The authenticated GitHub connector and exact remote mirror agree on four
commits. All four contain the same historical workflow definition, which has
both `push` and `pull_request` triggers. Connector queries covered every commit
but are explicitly limited to the first page of pull-request-triggered runs;
they returned zero runs, consistent with the repository having no pull
requests, but cannot prove the push-run history.

A repository-local GitHub CLI was unpacked under `development/local/` without a
system installation. The structural baseline, tool hashes and rollback
metadata are Git-ignored. No workflow log or artifact export has been claimed:
the status remains `BLOCKED` with
`GITHUB-ACTIONS-COMPLETE-RUN-ENUMERATION-AUTH-REQUIRED`.

A 2026-09-01 preflight reconfirmed that authenticated SSH can read exactly the
single advertised `main` ref and that the repository is not anonymously
readable. The existing GitHub API credential is no longer valid, however, and
the configured HTTPS Git credential-helper executable is absent. Neither path
can enumerate Actions runs, jobs, logs or artifacts. The aggregate preflight
receipt remains Git-ignored; no credential value, remote write or visibility
change occurred.

GitHub documents that complete run, job-log and artifact reads for a private
repository can use a fine-grained token restricted to this repository with only
`Actions: read`. The credential must be supplied outside Git and chat. Classic
OAuth `repo` scope is broader and is not the preferred path.

All four commits were about two days old at preflight time, so retained logs
are expected to remain downloadable. The workflow does not call
`actions/upload-artifact` or `actions/download-artifact`, but artifact count
still requires authenticated API enumeration; YAML inspection is not accepted
as proof of zero artifacts.
