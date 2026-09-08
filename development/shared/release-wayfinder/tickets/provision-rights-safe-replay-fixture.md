---
title: Provision the rights-safe replay fixture and execution environments
label: wayfinder:task
mode: HITL
status: open
blocked_by:
  - Bind historical validation to current-toolkit contracts
  - Freeze the three Primary Profile stacks
  - Complete the private-literal and full-history publication audit
---

## Question

Can all three Primary Profiles be supplied with an authorized Rights-safe Replay
Input, exact source/target environments, backup/artifact roots, Package CARLA
target, vanilla UE4.27 target and second clean project while keeping all private
assets and binary dependencies outside Git?

## Current progress

An original text-only L1 quickstart now exercises inspect, plan, plan verification
and the expected runtime `NOT_RUN` safe stop in an explicit temporary directory.
It commits no generated map or binary asset. This ticket remains open because
that host-logic demonstration is not a redistributable Editor/runtime fixture
for any of the three Primary Profiles.
