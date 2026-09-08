# Execution contexts

| Context | Use | Fast-fail boundary |
|---|---|---|
| `host-cpython` | JSON, paths, hashes, plans, archives, reports | Never load or mutate Unreal assets |
| `source-unreal-python` | Source CARLA Asset Registry, dependencies, Unreal API migration | Never assume vanilla UE4.27 classes |
| `ue427-unreal-python` | Target assets, redirectors, World/PIE/cold-copy | Never depend on CARLA fork classes |
| `carla-client-python` | Server/client, map, spawn, TM, walker, runtime probes | Client/server versions must match |
| `shell-build` | Version-resolved import/package/commandlet launch | Do not invent commands from memory |

Set `CMTK_EXECUTION_CONTEXT` for every command. `inspect`, `plan`, `validate`,
`verify-plan`, archive audit and performance comparison require
`host-cpython`. External evidence uses two steps:

1. run `scripts/context_receipt.py` through the planned Unreal, CARLA client or
   shell execution context to finalize a private receipt; this standard-library
   boundary file uses Python 3.7-compatible syntax and never executes a
   migration or repair;
2. run `record-stage-evidence` in `host-cpython` to verify the finalized receipt,
   plan, hashes, check contract, backup/rollback and redaction before atomically
   writing the public-safe stage/check bundle.

A compatible external Python runner may call `record-stage-evidence` directly;
it then probes the live API instead of accepting a finalized boundary receipt.
Any mismatch returns `ENV-EXECUTION-CONTEXT-MISMATCH` or a stable `ADAPTER-*`
reason code.
