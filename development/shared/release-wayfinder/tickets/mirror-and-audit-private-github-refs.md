---
title: Mirror and audit every private GitHub ref
label: wayfinder:task
mode: AFK
status: closed
assignee: codex
blocked_by:
  - Supply and approve the authoritative private literal set
---

## Question

Can an authenticated enumeration and mirror of all GitHub-only branches, tags,
pull-request refs and other publication-visible refs prove that their names and
reachable objects pass the approved private-literal audit without publishing
the mirror or its contents?

## Resolution

Yes, for the point-in-time private repository state. The authenticated GitHub
connector completed two branch pages and reported one default branch and no
pull requests. An independent authenticated SSH enumeration reported one head,
no tags, no pull-request refs and no other advertised refs. A fresh bare mirror
contained the same single ref, and a final refresh proved an exact ref-name and
object-ID match with the remote.

The mirror's 187 reachable objects and the ref name were scanned against the
owner-approved 60-entry private literal set with zero findings. `git fsck
--full --strict` passed, the symbolic `HEAD` resolved to the mirrored ref, and
the historical path inventory contained no `.uasset`, `.umap`, `.uexp`,
`.ubulk`, `.pak` or platform binary paths.

The mirror, detailed audit reports, set fingerprints and rollback metadata are
Git-ignored under `development/local/`. This resolution does not cover GitHub
Actions logs or artifacts, the current dirty worktree, future refs or the final
clean-clone publication gate. No remote write, push, release, publication or
visibility change was performed.

On 2026-09-01 a non-interactive SSH recheck still advertised only the same
single `main` object previously mirrored and audited. This preserves the
point-in-time result for the current remote ref set; GitHub API authentication
was separately found invalid and remains an Actions-export blocker.
