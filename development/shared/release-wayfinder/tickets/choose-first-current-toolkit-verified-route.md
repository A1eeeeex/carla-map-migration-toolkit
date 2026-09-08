---
title: Choose the first current-toolkit verified route
label: wayfinder:grilling
mode: HITL
status: closed
assignee: codex
blocked_by: []
---

## Question

Which one route will anchor `v0.1.0-rc`, based on user value, implementation
readiness, available environments and evidence cost, and what exact profile and
version stack must its current-toolkit replay accept?

## Resolution

There is no single release-anchor route. The maintainer requires route coverage
across all three supported migrations before `v0.1.0-rc`: one accepted Primary
Profile for RoadRunner to Source CARLA, Source CARLA to Package CARLA, and
Source CARLA to vanilla UE4.27. Secondary Profiles may remain explicitly
experimental; implementation order remains a separate engineering decision.

Read-only recovery found 19 post-Phase-A route/status evidence candidates. A
cross-route acceptance record reports 49 checks with no failed checks; Package
archive/install records form a hash chain, and UE4.27 cold-copy records bind
matching map and archive hashes. These facts corroborate the maintainer's prior
validation, but the records predate the current Toolkit evidence contracts and
do not become Current-toolkit Verified Runs by relabelling.

The successor task
[`Bind historical validation to current-toolkit contracts`](bind-historical-validation-to-current-toolkit-contracts.md)
will map every required check, establish what can be reused as characterization,
and identify the minimum current replay. The revised decision support is in
[`three-route-verification-decision-brief.md`](../../release-research/three-route-verification-decision-brief.md).
