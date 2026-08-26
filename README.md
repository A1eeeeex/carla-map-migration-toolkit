# CARLA Map Migration Toolkit

Three repeatable migration workflows for custom CARLA maps.

```text
RoadRunner    ── Import & Repair ──► Source CARLA
Source CARLA ── Cook & Verify ─────► Package CARLA
Source CARLA ── Detach & Repair ───► Vanilla UE4.27
```

This repository is an experimental, skills-only Codex Plugin plus a deterministic
host-side core. It inventories paths and versions, seals read-only plans, audits
archives, compares performance evidence, and preserves `NOT_RUN` when Unreal or
CARLA checks have not happened. It does not distribute maps, XODR, Unreal/CARLA
binaries, or engine assets.

> This is an independent community project. It is not affiliated with or
> endorsed by CARLA, Epic Games, or MathWorks RoadRunner.

## The three routes

| Route Skill | Outcome | Current public evidence |
|---|---|---|
| `roadrunner-to-source-carla` | Editable Source CARLA map and handoff | L0–L2 only; Editor/runtime NOT_RUN |
| `source-carla-to-package-carla` | Audited content/full package and runtime handoff | L0–L2 only; Cook/import/runtime NOT_RUN |
| `source-carla-to-ue427` | CARLA-detached UE4.27 map with mandatory cold-copy | L0–L2 only; Editor/PIE/cold-copy NOT_RUN |

No stack is marked verified. See [compatibility evidence](docs/compatibility/README.md).

## Plugin-first installation

Install the complete `plugins/carla-map-migration-toolkit` directory through a
Codex workspace/plugin marketplace. The local catalog is
`.agents/plugins/marketplace.json`. v0.1 does not support installing a single
Skill subdirectory because all three Skills share scripts, schemas, references,
profiles, templates, and status rules.

Current canonical Plugin/Skill structure follows the official OpenAI
[Plugins](https://developers.openai.com/plugins/concepts/plugins),
[Skills](https://developers.openai.com/plugins/concepts/skills), and
[build guidance](https://developers.openai.com/plugins/build/skills).

## Quick start

Invoke one route naturally and ask for inspection first:

```text
Use $roadrunner-to-source-carla. Inspect this RoadRunner Datasmith export and
plan its import into my Source CARLA build. Do not modify anything yet.
```

```text
Use $source-carla-to-package-carla. Inspect the Source handoff and plan a
matching Linux content package, including archive and runtime validation.
```

```text
Use $source-carla-to-ue427. Plan a migration into clean vanilla UE4.27, remove
CARLA-specific dependencies, and require a second clean-project cold-copy.
```

The deterministic host commands are also usable directly:

```bash
python3 plugins/carla-map-migration-toolkit/scripts/cmtk.py inspect \
  --route roadrunner-to-source-carla \
  --config plugins/carla-map-migration-toolkit/examples/map-workspace.example.json
```

The checked-in example contains illustrative absolute paths and will normally
return `BLOCKED` until copied and adapted to existing allowed roots. This is the
safe outcome.

## Safety model

- `inspect` and `plan` are the default; plans bind the entire workspace hash.
- Every path is canonicalized and checked against explicit allowed roots.
- External archives are inspected without extraction.
- Raw host operations on `.uasset`, `.umap`, `.uexp`, and `.ubulk` are forbidden.
- Unreal changes require engine APIs, referencer evidence, a backup, verification,
  and rollback metadata.
- Optimization requires comparable conditions and protected-property hashes.
- `PASS`, `WARN`, `FAIL`, `NOT_RUN`, `NOT_APPLICABLE`, and `BLOCKED` are the only
  statuses; `NOT_RUN` never becomes success.

See the shared [safety guardrails](plugins/carla-map-migration-toolkit/references/safety-guardrails.md)
and [evidence levels](plugins/carla-map-migration-toolkit/references/evidence-levels.md).

## Development verification

```bash
python3 -m pip install --requirement requirements-dev.txt
python3 -m pytest -q
```

Hosted CI is limited to L0–L2 structure, logic, and anonymous fixtures. Unreal
Editor, CARLA runtime, Cook/import, PIE, and cold-copy require authorized
self-hosted environments and separate evidence.

## Project status

This tree is an implementation candidate, not `v0.1.0-rc`: no real end-to-end
public replay has passed, the RoadRunner version is unknown, and a project license
has not been selected. See [known limitations](KNOWN_LIMITATIONS.md) and
[verification status](VERIFICATION_STATUS.md).
