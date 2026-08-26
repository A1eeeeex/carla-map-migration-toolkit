# Performance protocol

Performance work is optional and starts only after functional validation.

Use identical hardware, OS, target profile, resolution, quality, camera profile,
traffic/sensor load, warmup frames, sample frames, repeats, VSync, and FPS cap.
Report FPS and frame time plus available game/render/GPU thread, RAM/VRAM,
actor, primitive, and draw-call metrics.

Preserve LOD0, material slots, transforms, road geometry, XODR, and drivable
collision. Do not merge or delete roads, lane markings, traffic facilities,
Route Planner, triggers, or independently semantic objects by default. Actor
merge, ISM/HISM, texture downsampling, auto-LOD, vegetation pruning, and
collision-complexity changes are `REVIEW_REQUIRED`.

Run `compare-performance` only on snapshots with identical `conditions`.
Protected hash changes fail even if frame time improves. VSync or an FPS cap
adds a warning; missing or non-improving frame-time evidence fails.
