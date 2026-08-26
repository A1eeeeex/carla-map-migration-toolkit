# ADR-001: three route Skills in one Plugin

Status: accepted for v0.1.

Use exactly three top-level Skills matching the real source/target transitions.
Keep repair, validation, performance, status, path, and evidence logic at Plugin
level. Do not add umbrella, performance-only, Map Doctor, Apollo, MCP, or general
Unreal Skills without new evaluation evidence.

Implementation priority follows available evidence: Source CARLA to UE4.27,
Source CARLA to Package CARLA, then RoadRunner to Source CARLA. All remain
experimental until the required real replay level is recorded.
