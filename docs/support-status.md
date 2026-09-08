# Support status

| Status | Meaning |
|---|---|
| `planned` | Contract and route are defined, but implementation is incomplete. |
| `implemented` | Code and relevant L0-L2 tests exist; no real-route success is implied. |
| `maintainer-verified` | A maintainer produced a complete evidence record in the required real environment. |
| `community-verified` | An external user produced contract-complete evidence accepted by a maintainer. |
| `experimental` | Partial implementation/evidence exists without a stable compatibility commitment. |
| `unsupported` | The combination or behavior is explicitly outside the supported scope. |
| `unknown` | Evidence or identity is insufficient. |

For Source CARLA → UE4.27, `maintainer-verified` additionally requires a second,
independent vanilla UE4.27 project cold-copy. `NOT_RUN` is a check result and
never aggregates to PASS.
