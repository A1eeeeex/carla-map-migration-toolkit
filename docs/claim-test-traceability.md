# Claim → test → evidence traceability

| Claim ID | Required level | Test/eval IDs | Required evidence | Current status |
|---|---:|---|---|---|
| C-PLUGIN-001 | L0 | T-PLUGIN-STRUCTURE | Plugin validator/test report | implemented |
| C-ROUTE-001 | L2 | T-ROUTE-STATIC-EVAL | Trigger/behavior eval results | implemented |
| C-SAFE-001 | L2 | T-PATH-SAFETY; T-PLAN-STALE; T-BACKUP-MANIFEST | Unit/adversarial report | implemented |
| C-EVID-001 | L3 | T-EVIDENCE-SCHEMA; T-NOT-RUN-AGGREGATION | Stage results + real route | experimental |
| C-SRC-UE427-001 | L5 | T-UE427-EDITOR; T-UE427-PIE; T-UE427-COLD | Verified run + target/cold validation | planned |
| C-UE427-REF-001 | L5 | T-UE427-REF-TARGET; T-UE427-REF-COLD | Reference audits | planned |
| C-UE427-MAT-001 | L5 | T-UE427-MATERIAL-TARGET; T-UE427-MATERIAL-COLD | Material audits + authorized screenshots | planned |
| C-UE427-ENV-001 | L5 | T-UE427-REOPEN; T-UE427-PIE; T-UE427-ENV-COLD | Target/cold validation | planned |
| C-UE427-COL-001 | L5 | T-UE427-COLLISION-TARGET; T-UE427-COLLISION-COLD | Collision audits | planned |
| C-SRC-PKG-001 | L5 | T-PKG-COOK; T-PKG-IMPORT; T-PKG-RUNTIME | Verified run | planned |
| C-RR-SRC-001 | L4 | T-RR-IMPORT-EDITOR; T-RR-RUNTIME | Verified run | planned |
| C-PERF-001 | L4 | T-PERF-COMPARABLE; T-PERF-PROTECTED-DIFF | Controlled real profile | experimental |

Evidence absence downgrades status. A new major CARLA/Unreal/RoadRunner version
requires a separate verified run; compatibility is not inherited across stacks.
