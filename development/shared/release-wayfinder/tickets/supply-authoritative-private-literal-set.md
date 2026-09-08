---
title: Supply and approve the authoritative private literal set
label: wayfinder:grilling
mode: HITL
status: closed
assignee: codex
blocked_by: []
---

## Question

What complete, owner-approved set of private customer, project, map, host and
credential literals can be derived from the original private materials and
kept outside the publication candidate for the final history audit?

## Progress

The owner authorized generation of a local-only review candidate. The candidate
was derived from all 19 hash-verified original sources plus the two private
planning inputs, normalized using the publication audit's NFC and case-folding
contract, and kept below `development/local/`, which is Git-ignored and excluded
from the publication allowlist.

The normalized candidate contains 60 unique literals. A read-only local scan
found no matches in the 179 allowlisted publication-candidate files, 637 locally
reachable Git objects, or four local refs. This is not the final publication
audit: exact owner review, the authenticated GitHub Actions export, the
authenticated GitHub-only ref mirror, and the clean-clone gate remain required.

A supplemental high-confidence coverage scan found no Windows or UNC paths,
email addresses, non-loopback IP addresses, external URLs, explicit private
host assignments, cloud or GitHub access tokens, or quoted secret assignments.
The single IPv4-shaped value was a loopback address and was intentionally not
added to the private set.

## Resolution

The repository owner reviewed and approved the 60-entry normalized private
literal set. The plaintext set, candidate manifest, owner-approval receipt and
rollback metadata remain Git-ignored under `development/local/`; only this
aggregate resolution belongs to the publication candidate.

This closes the authoritative-input question for downstream audits. It does
not prove the final publication gate: the complete authenticated GitHub Actions
export, authenticated GitHub-only ref mirror and clean-clone audit remain
separate required tickets. No push, release, publication or visibility change
was authorized or performed.
