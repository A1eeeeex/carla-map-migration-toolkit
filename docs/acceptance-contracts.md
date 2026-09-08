# Route acceptance contracts

Every required check is independent. A required `FAIL` fails the route; a
required `NOT_RUN` makes it incomplete. Process exit code, screenshots or an
Editor opening alone cannot satisfy a route contract.

## RoadRunner → Source CARLA

Required evidence includes exact tool/plugin/CARLA/UE identities, committed and
saved imported assets, map/XODR correspondence, Editor open, spawn/topology
checks, road collision, material/reference audits, runtime smoke and a Source
handoff. The expected level is L4 before maintainer verification.

## Source CARLA → Package CARLA

Required evidence includes an accepted Source handoff, platform/version match,
cook configuration and dependency audit, artifact hashes, archive safety,
target backup/import, map registry and runtime load, materials, road collision,
OpenDRIVE/spawn checks, dynamic smoke and rollback. The expected level is L5.

## Source CARLA → vanilla UE4.27

Required evidence includes Source asset/dependency inventories, Unreal-safe
migration action records, target Asset Registry results, zero required missing
assets/materials and disallowed CARLA references, a complete runtime-class
replacement matrix, World Settings/environment, road collision, target reopen,
PIE, handoff, and a second clean-project cold-copy. C-SRC-UE427-001 cannot become
`maintainer-verified` below L5.
