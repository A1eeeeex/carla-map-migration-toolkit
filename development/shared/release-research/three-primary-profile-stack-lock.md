# Three Primary Profile stack lock

Date: 2026-08-28

## Decision

The exact component identities for the three v0.1 Primary Profiles are locked.
This closes the version-discovery question; it does not accept the current
external environments and does not create a Verified Run.

Every current replay must match the identities and fingerprints below. A
missing or different identity is `BLOCKED`, not a compatible fallback. CARLA,
Unreal Engine and RoadRunner components remain external dependencies and are
not redistributed by this repository.

## Shared host

| Component | Locked identity |
|---|---|
| Host | Ubuntu 22.04, Linux x86_64 |
| Host runtime | CPython 3.13.11 |
| CARLA client runtime | CPython 3.10.12 |
| C library | glibc 2.35 |
| Host fingerprint | `f14fbe3da6ea73c022b2c26aa37a74e80fc0515c3163ef9bd5cfbe04b641391e` |

GPU and driver identity are run-bound fields because a current runtime has not
started. They must be recorded before performance or visual evidence can pass.

## RoadRunner to Source CARLA

Primary Profile: `roadrunner-datasmith`. Required level: L4.

| Component | Locked identity |
|---|---|
| RoadRunner | `R2025a`, recovered from the project's `SavedWith` metadata |
| Exporter | Built-in RoadRunner R2025a Datasmith export |
| RoadRunner project format | File version 4 |
| Datasmith document | Scene version 0.24, SDK version 4.26.1 |
| Exporter fingerprint | `a72a3566ea68225347e6c1306c7fed0c12ae23c127431239eb02b64e891e06c4` |
| Source CARLA | `0.9.16`, commit `294096eb1c38eabf246e4f3a9cdab704e33a7f4c` |
| Source Unreal | CARLA fork 4.26.2, commit `e22f1e24769303a898b68e574f9856acfc78afeb` |
| Source Editor build ID | `12bcac7923d802f1` |
| Source Editor SHA-256 | `66497296854374a110c2ea3527d0df26a514041ed82dfbbc5230d114e4fbb519` |
| Source CARLA Python client | `0.9.16`, CPython 3.10, Linux x86_64 |
| Source client wheel SHA-256 | `eedb80e0ee339ad5ddd0e0c4b8b8a714a0f9c58286cd779385c70112941e3623` |
| RoadRunner integration | External plugin bundle version `1.4.4` |
| Integration bundle fingerprint | `900dde638f5fd0c361aab1775606425519571b62753a981bae546020c9288f82` |
| Source stack fingerprint | `1da3aa9ced3561335b7b73ee1cf0d19d065a13974cdc6e147aee90d776ce5d4d` |

The integration bundle is locally fingerprinted but untracked and lacks
redistribution authorization. It must stay outside Git. A Rights-safe Replay
Input with the locked export metadata is still required.

## Source CARLA to Package CARLA

Primary Profile: `content-package`. Required level: L5.

| Component | Locked identity |
|---|---|
| Source CARLA / Unreal | The locked Source stack above |
| Package CARLA | `0.9.16`, Linux x86_64 |
| Package server build ID | `a2c9953feee9e013` |
| Package server SHA-256 | `03bcd413615fa1fc61a5b846342dbdc4e6b3541320a40d6bf17ff927039731f9` |
| CARLA Python client | `0.9.16`, CPython 3.10, manylinux x86_64 |
| Client wheel SHA-256 | `cd3f70a6c01793654ad4905813d03fcd20ad55a0343095d89eee3ccf78835d84` |
| Package stack fingerprint | `65c57e69e7a1b12c710f6da488a6f027f0a1fa733c16732b0a2aa69548292717` |

The client and server versions match at `0.9.16`. The existing Package target
still needs a reviewed baseline, backup root and unique rights-safe map identity
before import or runtime validation.

## Source CARLA to vanilla UE4.27

Primary Profile: `standalone-map`. Required level: L5.

| Component | Locked identity |
|---|---|
| Source CARLA / Unreal | The locked Source stack above |
| Target Unreal | Vanilla UE 4.27.2, commit `3abfe77d0b24a6d8bacebd27766912e5a5fa6f02` |
| Target Editor build ID | `38e3cf325968add2` |
| Target Editor SHA-256 | `6ed8177edda0592615dff56947c200b4e13e8bdb067cd9a0b0eee828db1f87c5` |
| Target engine fingerprint | `4b53623cdd37e8659d81ed6788753d90c170aa7a19fa07e53ca24bdafcf1745a` |

The primary target project and the second clean cold-copy project are run-bound
identities. Neither has been selected, so L5 remains `NOT_RUN`.

## Current readiness

All version and component identities are known, but the observed environments
are `FOUND_NOT_ACCEPTED`:

- Source CARLA and both Unreal worktrees contain tracked user changes;
- the Source tree contains untracked content whose publication rights are not
  established;
- the Package target has no accepted current baseline;
- no Rights-safe Replay Input, primary UE4.27 project or second clean project is
  selected;
- the current Toolkit snapshot is not frozen while release work is uncommitted;
- Source Unreal, UE4.27 Unreal, CARLA client and shell-build adapters have not
  produced current evidence.

At replay time, the Toolkit snapshot, input, source project, Package target,
primary UE4.27 project, cold-copy project, GPU and driver must be fingerprinted
and bound into the current workspace and Verified Run. No dirty or unknown
identity is silently accepted.
