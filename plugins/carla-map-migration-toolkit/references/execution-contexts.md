# Execution contexts

| Context | Use | Fast-fail boundary |
|---|---|---|
| `host-cpython` | JSON, paths, hashes, plans, archives, reports | Never load or mutate Unreal assets |
| `source-unreal-python` | Source CARLA Asset Registry, dependencies, Unreal API migration | Never assume vanilla UE4.27 classes |
| `ue427-unreal-python` | Target assets, redirectors, World/PIE/cold-copy | Never depend on CARLA fork classes |
| `carla-client-python` | Server/client, map, spawn, TM, walker, runtime probes | Client/server versions must match |
| `shell-build` | Version-resolved import/package/commandlet launch | Do not invent commands from memory |

Set `CMTK_EXECUTION_CONTEXT` for the bundled host command. Its default and only
accepted context is `host-cpython`; any mismatch returns
`ENV-EXECUTION-CONTEXT-MISMATCH`.
