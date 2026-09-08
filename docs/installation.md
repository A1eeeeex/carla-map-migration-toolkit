# Installation

## Supported package shape

The v0.1 distribution unit is this repository as one Codex marketplace
containing the complete `carla-map-migration-toolkit` Plugin. Install the whole
Plugin so its three route Skills share the same scripts, schemas, profiles,
references and templates.

Installing one Skill directory, copying files into a global Skills directory,
installing from PyPI, and downloading CARLA or Unreal binaries through this
project are not supported installation paths.

The repository marketplace layout follows OpenAI's official
[plugin packaging guidance](https://developers.openai.com/plugins/build/plugins).
The commands below were checked with Codex CLI 0.153.4. Install or update Codex
using the [official CLI guide](https://developers.openai.com/codex/cli/).
The previously tested 0.148.0 could list/install plugins, but the service now
rejects its use with the current default model. Plugin installation and model
access are separate checks; a successful `plugin list` does not prove both.

## Supported host contract

The first supported installation host is intentionally narrow:

| Component | v0.1 contract |
|---|---|
| Host | Ubuntu 22.04.5 LTS on x86_64 |
| Codex | Codex CLI 0.153.4 with `plugin marketplace add`, `plugin add`, and `plugin list` commands |
| Python | Python 3.10.12 |
| Git | Git 2.34.1 |
| Runtime dependency | `jsonschema==4.26.0`, installed into a repository-local virtual environment |

This is the observed test baseline, not a reason to reject a different Git or
OS patch before checking the actual commands. Other hosts and versions have
not been established by this rehearsal; macOS, Windows, desktop, IDE and
Codex Cloud installation remain `NOT_RUN`, not supported claims.
The Plugin does not install CARLA, Unreal Engine, RoadRunner, their Python
clients, or any map assets.

## Five-minute clean-clone installation

For a maintainer-provided text-only source archive, verify its `SHA256SUMS`,
unpack it into a dedicated empty directory and use the included repository-root
folder for the same commands. The local marketplace installation does not
require Git history; do not use the private build directory or an installed
Plugin cache as the distribution. The source-archive rehearsal used an allowlisted
snapshot; a later exact local clone of commit `6222f0c` also passed runtime setup,
the host demo and isolated Plugin installation.

Run these commands from a fresh clone. Do not use `sudo`, a global Python
environment, or a single Skill subdirectory. Environment setup and Plugin
installation use the `shell-build` execution context; the final deterministic
CLI check runs in `host-cpython`.

```bash
python3.10 --version
codex --version
codex plugin --help

python3.10 -m venv .venv
.venv/bin/python -m pip install --requirement requirements-runtime.txt

codex plugin marketplace add . --json
codex plugin add carla-map-migration-toolkit@carla-map-migration-toolkit --json
codex plugin list --marketplace carla-map-migration-toolkit --json

CMTK_EXECUTION_CONTEXT=host-cpython .venv/bin/python \
  plugins/carla-map-migration-toolkit/scripts/cmtk.py --help
```

An optional rights-safe L1 smoke then exercises inspection, plan sealing, plan
verification and the expected runtime-evidence safe stop without CARLA, Unreal
or customer assets:

```bash
demo_root="$(mktemp -d -t cmtk-quickstart.XXXXXX)"
.venv/bin/python demo/quickstart/run_demo.py --workspace-root "$demo_root"
```

The result must report `demo_status: PASS` and
`route_validation_status: NOT_RUN`. The latter is expected and must not be
relabeled as an Editor or runtime success.

The list result must identify `carla-map-migration-toolkit` as installed and
enabled. A new Codex session must then discover all three route Skills. Launch
Codex from the activated environment so `python3` resolves the runtime
dependency:

```bash
source .venv/bin/activate
codex
```

Start with a read-only request such as:

```text
Use $carla-map-migration-toolkit:source-carla-to-ue427. Inspect my Source CARLA handoff and plan a migration
to clean vanilla UE4.27. Do not modify anything yet.
```

## Evidence boundary

The September 1 rehearsal tested Plugin 0.1.0 installation and canonical route
selection on CLI 0.148.0. The September 5 follow-up installed CLI 0.153.4 only
in a task-private directory and passed an 11-case description-routing batch.
That batch is not an installed-invocation precision/recall benchmark.

The exact-clone installation and hosted test results for commit `6222f0c` are
summarized in [current status](current-status.md). Earlier preparation records
remain in the [release checklist](release-readiness.md). Repeat affected checks
when files or the declared environment change; no engine launch is needed to
validate Plugin installation or the anonymous demo. These checks do not establish
full installed-use routing accuracy or end-to-end engine compatibility.
