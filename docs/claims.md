# Public claims

The machine-readable source is
[`claims-registry.example.json`](../plugins/carla-map-migration-toolkit/examples/claims-registry.example.json).
This page summarizes current claims; it does not upgrade their status.

| Claim ID | Capability | Required evidence | Current status |
|---|---|---:|---|
| C-PLUGIN-001 | Local Plugin marketplace discovery | L0 | implemented |
| C-ROUTE-001 | Three request classes route to three distinct Skills | L2 | implemented |
| C-SAFE-001 | Host write plans use path, stale-plan and backup guards | L2 | implemented |
| C-EVID-001 | Machine-readable stage evidence with no exit-code-only success | L3 | experimental |
| C-SRC-UE427-001 | Source CARLA → vanilla UE4.27 with second clean-project cold-copy | L5 | planned |
| C-UE427-REF-001 | Disallowed CARLA references reach zero in target and cold-copy | L5 | planned |
| C-UE427-MAT-001 | Required materials/textures remain complete | L5 | planned |
| C-UE427-ENV-001 | World Settings/environment reopen and run in PIE | L5 | planned |
| C-UE427-COL-001 | Road collision passes target and cold-copy smoke tests | L5 | planned |
| C-SRC-PKG-001 | Source CARLA → matching Package CARLA | L5 | planned |
| C-RR-SRC-001 | Supported RoadRunner import parts → Source CARLA | L4 | planned |
| C-PERF-001 | Controlled optimization with protected-property rejection | L4 | experimental |

`implemented` means code and L0-L2 tests exist; it is not proof that a real map
migration succeeded. No current route has a verified run.
