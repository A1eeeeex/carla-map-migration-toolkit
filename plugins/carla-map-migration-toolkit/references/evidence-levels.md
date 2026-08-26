# Evidence levels and status

| Level | Meaning |
|---|---|
| `L0_STRUCTURE` | Plugin, Skill, schema, metadata, and link structure |
| `L1_LOGIC` | Deterministic host logic such as path/hash/archive/status/report |
| `L2_FIXTURE` | Anonymous fake-directory and fake-archive integration |
| `L3_EDITOR` | Real Source CARLA or UE4.27 Editor execution |
| `L4_RUNTIME` | Real Package CARLA, CARLA API, or PIE execution |
| `L5_PORTABILITY` | New environment or second clean-project cold-copy |

Statuses are exactly `PASS`, `WARN`, `FAIL`, `NOT_RUN`, `NOT_APPLICABLE`, and
`BLOCKED`. A lower evidence level never proves a higher one. `NOT_RUN` is not a
passing status. UE4.27 route acceptance requires L5 cold-copy evidence.
