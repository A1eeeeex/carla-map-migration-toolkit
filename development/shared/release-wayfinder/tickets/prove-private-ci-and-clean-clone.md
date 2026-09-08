---
title: Prove private CI and clean-clone installation on the release candidate
label: wayfinder:task
mode: AFK
status: open
blocked_by:
  - Define the public installation and distribution contract
  - Complete the private-literal and full-history publication audit
  - Export and audit the private GitHub Actions history
  - Mirror and audit every private GitHub ref
---

## Question

Does the exact private release-candidate commit pass hosted L0-L2 CI and, from
a disposable clean clone using only documented public inputs, install the
Plugin, list it as installed/enabled, discover all three Skills in a new Codex
session, run the structure tests and host-core help, produce the expected
anonymous dry-run result, and leave no generated or unlisted publication files?

## Current progress

On 2026-09-01 an allowlisted snapshot of the uncommitted public candidate passed
the documented Python 3.10.12 runtime install, host-core help, isolated Codex
0.148.0 marketplace add, Plugin 0.1.0 install/list as enabled, rights-safe
anonymous quickstart and all 379 tests. The installed Plugin tree matched the
snapshot Plugin tree apart from runtime bytecode caches, and the real Codex
configuration remained unchanged.

After correcting the public examples to use Plugin-qualified Skill names,
three independent ephemeral read-only Codex sessions selected the expected
Skill for one canonical prompt on each route. This closes discovery for the
snapshot rehearsal, not for an immutable release commit.

This ticket remains open. The rehearsal is not the exact release-candidate
commit, and hosted CI for that commit is unavailable until an authorized push.
