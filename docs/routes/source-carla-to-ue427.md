# Source CARLA to UE4.27

Use the `source-carla-to-ue427` Skill. Unreal assets must migrate through engine
APIs. Primary-project success is insufficient; a second clean-project cold-copy
is mandatory. The first current-toolkit UE4.27 `TARGET_VALIDATE` candidate was
withdrawn after strict log review found a virtual-texture parameter mismatch.
After a bounded eight-texture Unreal-API repair, a fresh UE4.27.2 replay passed
target reopen, inventory, zero material/type/compiler errors, sampled Editor/PIE
road collision, 180 PIE frames and five fixed-view review checks. The six-check
receipt was context-finalized and host-recorded privately. Asset replacement
provenance, repair-stage binding and current-contract cold-copy remain
`NOT_RUN`, so there is still no complete L5 Verified Run.

A post-repair matched LOD diagnostic also completed under one fixed offscreen
Editor protocol. Mean and tail frame times improved, but median frame time
improved only 0.56% against a sealed 3% automatic threshold. The result is
therefore `REVIEW_REQUIRED`; it is not a packaged-runtime, general-map or L5
performance claim.

Recovered historical records include target/collision/visual signals and a
second clean-project cold-copy consistency chain. They confirm prior validation
but are not yet a current-contract L5 Verified Run. Already-repaired content
should be re-audited rather than destructively repaired again solely to recreate
evidence.

Planning requires explicit, in-root Source handoff, asset inventory, dependency
manifest, route manifest, and XODR files. Their sizes and SHA-256 values are
sealed into the plan and rechecked before it can verify.

Private map identity, paths, screenshots, raw logs and binary assets are not
published. The sanitized target-stage candidate remains outside
`evidence/verified/` until it can be assembled into a complete accepted route.
