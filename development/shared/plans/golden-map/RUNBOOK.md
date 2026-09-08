# Golden Map staged runbook

This is a future execution protocol, not evidence that a run occurred. Use the
[installation guide](../../../../docs/installation.md) and select just the
requested route. Keep workspaces, assets, receipts and raw captures outside Git.

## 1. Inspect and plan

Confirm [inputs](INPUT_CONTRACT.md) and [rights](RIGHTS_CHECKLIST.md), then run
from the installed clone in host-cpython. Replace angle-bracket values locally:

```bash
CMTK_EXECUTION_CONTEXT=host-cpython .venv/bin/python plugins/carla-map-migration-toolkit/scripts/cmtk.py inspect --route <route-id> --config <workspace.json>
CMTK_EXECUTION_CONTEXT=host-cpython .venv/bin/python plugins/carla-map-migration-toolkit/scripts/cmtk.py plan --route <route-id> --config <workspace.json> --output <artifact-root>/route-plan.json
CMTK_EXECUTION_CONTEXT=host-cpython .venv/bin/python plugins/carla-map-migration-toolkit/scripts/cmtk.py verify-plan --config <workspace.json> --plan <artifact-root>/route-plan.json --plan-sha256 <sealed-plan-hash>
```

A blocked inspection is not permission to apply. Review scope, backups, target
conflicts and rollback before any authorized Editor/API action. Input changes
invalidate the sealed plan; do not edit its hash to make it pass.

## 2. Run only the selected route

- RoadRunner to Source: use the [import route](../../../../docs/routes/roadrunner-to-source-carla.md);
  distinguish Dataprep preview from Import / Execute / Commit / Save. Source
  Unreal Python handles asset checks; a matching carla-client-python handles runtime.
- Source to Package: use the [package route](../../../../docs/routes/source-carla-to-package-carla.md);
  resolve version-specific build/import commands in shell-build, audit before
  extraction, back up the matching target and independently load/run the map.
- Source to UE4.27: use the [detachment route](../../../../docs/routes/source-carla-to-ue427.md);
  query referencers, repair through Unreal APIs, then repeat target checks in
  a second clean project in ue427-unreal-python. Archive parity alone is not cold-copy.

Wait for adequate VRAM before a heavy launch. Consolidate camera, collision and
runtime checks into a bounded session. Do not kill unrelated processes or replay
all routes for one changed material. Preserve failures and rollback metadata.

## 3. Record, validate and publish selectively

Use [existing context receipts](../../../../docs/evidence-adapters.md) and the
[evidence checklist](EVIDENCE_CHECKLIST.md), not invented PASS files.
The host `validate` command only creates a pending NOT_RUN report; it does not
run the checks above. Once real checks exist, validate their schema/hash/route
bindings using the existing receipt and Verified Run contracts.

Capture only authorized views from [capture checklist](CAPTURE_CHECKLIST.md).
Link each public image/caption to its reviewed evidence. Promote only the exact
checked route/profile/stack, never all three at once because one succeeded.
