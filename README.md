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

The [capability checklist](docs/capabilities.md) distinguishes automated checks
from guided Editor work. It includes Content-only delivery audits, SHA256
manifests and per-counter performance comparisons without launching an engine.

> This is an independent community project. It is not affiliated with or
> endorsed by CARLA, Epic Games, or MathWorks RoadRunner.

## The three routes

| Route Skill | Outcome | Recovered historical validation | Current-contract evidence |
|---|---|---|---|
| `roadrunner-to-source-carla` | Editable Source CARLA map and handoff | Source Editor and bounded flat-road driving records recovered | Complete L4 Verified Run not yet recorded |
| `source-carla-to-package-carla` | Audited content/full package and runtime handoff | Package/install/runtime hash chain recovered | Complete L5 Verified Run not yet recorded |
| `source-carla-to-ue427` | CARLA-detached UE4.27 map with mandatory cold-copy | Second-project structural, PIE, sunny-view and Content-only delivery records recovered | Target-stage evidence exists; complete current-contract L5 Verified Run not recorded |

All three routes have recorded real-use evidence, with different coverage and
limitations. Later records also include a second clean UE4.27.2 project and a
Content-only delivery; the older statement that no cold-copy work had happened
was stale. These case records are not complete current-contract Verified Runs,
and no version stack is marked verified. See the [current status](docs/current-status.md),
[release checklist](docs/release-readiness.md),
[historical binding](development/shared/release-research/historical-evidence-binding-summary.md),
[repair/optimization recovery](development/shared/release-research/historical-repair-optimization-evidence-summary.md),
and [compatibility evidence](docs/compatibility/README.md).

Public wording and route status are governed by the machine-readable
[Claims Registry](plugins/carla-map-migration-toolkit/examples/claims-registry.example.json),
the [support-status definitions](docs/support-status.md), and the
[claim-to-evidence matrix](docs/claim-test-traceability.md). `implemented` never
means that a real Editor/runtime migration has passed.

## Plugin-first installation

From a clean clone on the supported host, create the local Python runtime and
install this repository as one Codex marketplace and one complete Plugin. This
setup block uses the `shell-build` execution context; bundled deterministic
commands run in `host-cpython`.

```bash
python3.10 -m venv .venv
.venv/bin/python -m pip install --requirement requirements-runtime.txt
codex plugin marketplace add . --json
codex plugin add carla-map-migration-toolkit@carla-map-migration-toolkit --json
```

v0.1 does not support installing a single Skill subdirectory because all three
Skills share scripts, schemas, references, profiles, templates, and status
rules. See the exact host versions, verification command, limitations and
five-minute walkthrough in the [installation contract](docs/installation.md).

Current canonical Plugin/Skill structure follows the official OpenAI
[Plugins](https://developers.openai.com/plugins/concepts/plugins),
[Skills](https://developers.openai.com/plugins/concepts/skills), and
[build guidance](https://developers.openai.com/plugins/build/skills).

## Quick start

Run the [rights-safe host demo](demo/quickstart/README.md) without any CARLA,
Unreal or customer assets:

```bash
demo_root="$(mktemp -d -t cmtk-quickstart.XXXXXX)"
.venv/bin/python demo/quickstart/run_demo.py --workspace-root "$demo_root"
```

It should inspect and verify a sealed plan, then report runtime validation as
`NOT_RUN`. That safe stop is intentional: the synthetic text fixture proves L1
host behavior only, not a real map import.

Invoke one route naturally and ask for inspection first:

```text
Use $carla-map-migration-toolkit:roadrunner-to-source-carla. Inspect this RoadRunner Datasmith export and
plan its import into my Source CARLA build. Do not modify anything yet.
```

```text
Use $carla-map-migration-toolkit:source-carla-to-package-carla. Inspect the Source handoff and plan a
matching Linux content package, including archive and runtime validation.
```

```text
Use $carla-map-migration-toolkit:source-carla-to-ue427. Plan a migration into clean vanilla UE4.27, remove
CARLA-specific dependencies, and require a second clean-project cold-copy.
```

The deterministic host commands are also usable directly:

```bash
CMTK_EXECUTION_CONTEXT=host-cpython .venv/bin/python \
  plugins/carla-map-migration-toolkit/scripts/cmtk.py inspect \
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
- Stage/check statuses are exactly `PASS`, `WARN`, `FAIL`, `NOT_RUN`,
  `NOT_APPLICABLE`, and `BLOCKED`. Verified Run roll-ups use `PASS`,
  `PASS_WITH_WARNINGS`, `FAIL`, `INCOMPLETE`, and `BLOCKED`; a required
  `NOT_RUN`/`NOT_APPLICABLE` becomes `INCOMPLETE`, never success.
- L0–L5 are the complete proof-level scale. `community-verified` is a support
  maturity status, not a numeric evidence level, and still requires the route's
  full L4/L5 gate.
- A Verified Run check must bind to its route catalog stage and hashed underlying
  structured evidence; input/artifact parsing uses one byte snapshot, evidence
  paths stay repository-relative, and redaction scans the full public envelope
  without publishing the private term set.

See the shared [safety guardrails](plugins/carla-map-migration-toolkit/references/safety-guardrails.md)
and [evidence levels](plugins/carla-map-migration-toolkit/references/evidence-levels.md).
The external receipt flow is documented in
[execution-context evidence adapters](docs/evidence-adapters.md).

## Development verification

```bash
.venv/bin/python -m pip install --requirement requirements-dev.txt
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  .venv/bin/python -m pytest -q -p no:cacheprovider
```

Hosted CI is limited to L0–L2 structure, logic, and anonymous fixtures. Unreal
Editor, CARLA runtime, Cook/import, PIE, and cold-copy require authorized
self-hosted environments and separate evidence.

## Development materials

Versioned development notes belong in [`development/shared/`](development/shared/).
Original handoff, discovery, draft, and private material is consolidated under
the Git-ignored `development/local/` tree. See the
[development directory guide](development/README.md) before adding material.

## License

Original project material is licensed under the
[Apache License 2.0](LICENSE). Copyright and attribution details are recorded in
[NOTICE](NOTICE.md) and [CITATION.cff](CITATION.cff). The license does not grant
rights to CARLA, Unreal Engine, RoadRunner, customer material, private inputs,
excluded binaries, or third-party assets.

Public maintainer: [@A1eeeeex](https://github.com/A1eeeeex). Security reports
must use the private process in [SECURITY.md](SECURITY.md), not a public issue.

## Project status

This is an experimental implementation candidate, not a fully verified
`v0.1.0-rc`. Release preparation reuses recorded real work and tests only the
changed surfaces; it does not replay migrations merely to regenerate paperwork.
Performance results include regressions and declared workload limits, not
universal speedup claims. See the [release checklist](docs/release-readiness.md),
[known limitations](KNOWN_LIMITATIONS.md) and
[verification status](VERIFICATION_STATUS.md).
