---
title: Freeze the three Primary Profile stacks
label: wayfinder:task
mode: AFK
status: closed
assignee: codex
blocked_by:
  - Bind historical validation to current-toolkit contracts
---

## Question

What exact RoadRunner/exporter/integration-plugin, Source CARLA/source Unreal,
Package CARLA client/server and vanilla UE4.27 identities, operating systems and
artifact fingerprints define the accepted replay stack for each Primary
Profile, with every unresolved identity failing closed rather than inheriting a
historical assumption?

## Resolution

Read-only inspection locked RoadRunner `R2025a` with its built-in Datasmith
export identity, external integration bundle `1.4.4`, Source and Package CARLA
`0.9.16`, Source Unreal 4.26.2, vanilla Unreal 4.27.2, the Linux x86_64 host and
their component fingerprints. Package client/server versions match. The
[public stack lock](../../release-research/three-primary-profile-stack-lock.md)
defines the three exact combinations and fails closed on any mismatch.

The task became AFK because all technical identities were recoverable from
local metadata and binaries without a maintainer choice. Environment acceptance
remains separate: rights-safe inputs/projects, the Toolkit snapshot and current
execution-context evidence are still pending, and dirty external worktrees are
not silently accepted.
