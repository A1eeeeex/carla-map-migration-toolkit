# Planned real-map example

This is a development plan, not a runnable demo. It contains no map, OpenDRIVE,
RoadRunner export, Unreal asset, screenshot or third-party content.

## Start here

1. [Input contract](INPUT_CONTRACT.md) — what to provide locally, one route at a time
2. [Rights checklist](RIGHTS_CHECKLIST.md) — what may be shared
3. [Runbook](RUNBOOK.md) — inspect, plan and execute in the correct context
4. [Evidence checklist](EVIDENCE_CHECKLIST.md) — required proof and signoff
5. [Capture checklist](CAPTURE_CHECKLIST.md) — views to record after real checks

Map assets stay in a dedicated external workspace, not in this directory. This
framework is deliberately kept under development plans rather than runnable demos.

## Planned map

The future `public-golden-map-lite` should be small and rights-cleared: a
600–1,200 m road network with a curve, one junction, a slope change, 8–20 spawn
points, road collision, at least two material classes and a basic environment.
Each fault variant in `manifest.json` introduces one primary failure and declares
the expected reason code.

The full maintainer replay may use private RoadRunner/Unreal/CARLA inputs, but
only redacted evidence may enter this repository until redistribution rights are
confirmed. `REVIEW_REQUIRED` is not a license or permission to publish assets.
