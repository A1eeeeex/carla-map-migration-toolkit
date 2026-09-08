# CARLA Map Migration Toolkit

Three Codex Skills for importing, packaging and delivering custom CARLA maps.

```text
RoadRunner    ── Import & Repair ──► Source CARLA
Source CARLA ── Cook & Verify ─────► Package CARLA
Source CARLA ── Detach & Repair ───► Vanilla UE4.27
```

[中文](README.zh-CN.md) · [Installation](docs/installation.md) · [Capabilities](docs/capabilities.md) · [Evidence & limitations](docs/current-status.md)

An experimental Codex Plugin combining map-processing guidance with scripts for
inspection, planning, package audits and performance comparisons. It helps Codex
follow repeatable workflows; it is not a one-click converter. Imports, repairs,
builds and runtime checks still require your own tools and authorized Editor/API operations.

## Choose your route

| Your task | Route guide |
|---|---|
| Import a RoadRunner export into editable Source CARLA | [Import and repair](docs/routes/roadrunner-to-source-carla.md) |
| Build and validate a map for matching Package CARLA | [Cook and package](docs/routes/source-carla-to-package-carla.md) |
| Remove CARLA dependencies and deliver to vanilla UE4.27 | [Migrate and cold-copy](docs/routes/source-carla-to-ue427.md) |

Shared guidance covers materials, textures, references, collision, daylight,
Content-only delivery and staged performance optimization. Host scripts audit
archives, generate SHA256 manifests and report performance gains and regressions.
The [capability checklist](docs/capabilities.md) separates automation from Editor work.

## Install

Tested baseline: Ubuntu 22.04 x86_64, Python 3.10.12 and Codex CLI 0.153.4.
See [installation](docs/installation.md) for version checks and setup details.
Install the complete Plugin, not a single Skill folder: the three Skills share
scripts, schemas and references. Setup uses the `shell-build` context.

```bash
git clone https://github.com/A1eeeeex/carla-map-migration-toolkit.git
cd carla-map-migration-toolkit
python3.10 -m venv .venv
.venv/bin/python -m pip install --requirement requirements-runtime.txt
codex plugin marketplace add . --json
codex plugin add carla-map-migration-toolkit@carla-map-migration-toolkit --json
source .venv/bin/activate
codex
```

## Use with Codex

Choose one request, provide your input location, and start with inspection:

```text
Use $carla-map-migration-toolkit:roadrunner-to-source-carla. Inspect my RoadRunner export and plan its import into Source CARLA. Do not modify anything yet.
```

```text
Use $carla-map-migration-toolkit:source-carla-to-package-carla. Inspect my Source CARLA handoff and plan a matching content package. Do not build or install yet.
```

```text
Use $carla-map-migration-toolkit:source-carla-to-ue427. Inspect my Source CARLA map and plan delivery to clean UE4.27, including a second clean-project cold-copy. Do not modify anything yet.
```

No engine or map available? In a separate terminal at the clone root, try the
[synthetic host demo](demo/quickstart/README.md):

```bash
demo_root="$(mktemp -d -t cmtk-quickstart.XXXXXX)"
.venv/bin/python demo/quickstart/run_demo.py --workspace-root "$demo_root"
```

Expected: `demo_status: PASS`, `route_validation_status: NOT_RUN`.
The demo checks planning logic, not a real map import.

## What has been verified?

[435 automated tests passed for commit 6222f0c](https://github.com/A1eeeeex/carla-map-migration-toolkit/actions/runs/34193021128).
These cover structure, host logic and synthetic fixtures; engine jobs were skipped.
All three routes also have historical real-use records, including second-project
UE4.27 checks and Content-only delivery. Coverage is case-specific, not a guarantee
for every map or version. Complete end-to-end evidence under the toolkit's current
verification format is still missing; this remains experimental, not a certified RC.

See [evidence and compatibility](docs/current-status.md) for records and gaps.
Inspection and planning are the default. Asset changes require explicit approval,
engine-aware backups and validation; high-risk optimizations require review.
This repository includes no customer maps, XODR or engine binaries.

## Further reading

- [Known limitations](KNOWN_LIMITATIONS.md) — unsupported behavior and implementation gaps
- [Contributing](CONTRIBUTING.md) — development setup and change guidelines
- [Development reference index](development/shared/README.md) — design, evidence rules and historical reports
- [Changelog](CHANGELOG.md) — development and release history

<details>
<summary>Developer commands and direct CLI example</summary>

Run tests from the clone root:

```bash
.venv/bin/python -m pip install --requirement requirements-dev.txt
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
  .venv/bin/python -m pytest -q -p no:cacheprovider
```

Direct inspection runs in `host-cpython`:

```bash
CMTK_EXECUTION_CONTEXT=host-cpython .venv/bin/python \
  plugins/carla-map-migration-toolkit/scripts/cmtk.py inspect \
  --route roadrunner-to-source-carla \
  --config plugins/carla-map-migration-toolkit/examples/map-workspace.example.json
```

The example uses illustrative paths. Copy and adapt it to your allowed roots;
otherwise `BLOCKED` is expected. See [installation](docs/installation.md).

</details>

---

## License and contact

[Apache-2.0](LICENSE) · [Notice](NOTICE.md) · [Citation](CITATION.cff) · Maintainer [@A1eeeeex](https://github.com/A1eeeeex).
The license covers original project material, not third-party maps or engines.
This is an independent community project, not affiliated with or endorsed by
CARLA, Epic Games or MathWorks RoadRunner. Follow [SECURITY.md](SECURITY.md)
for security reports; do not disclose sensitive details in public issues.
