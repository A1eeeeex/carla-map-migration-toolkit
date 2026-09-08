# Contributing

Contributions should stay within one of the three migration routes or their
shared safety/repair/validation core. Do not add private assets or binaries.

## Start with a useful report

Use the bug, compatibility or feature form in GitHub Issues. Include the Toolkit
commit, route/Profile, exact CARLA/Unreal/RoadRunner versions where relevant,
OS/architecture, command and reason code. Separate host checks from actual
Editor/runtime observations; keep unrun checks explicit. Reproduction assets
are optional, never required. Share only original text fixtures or material
whose rights and privacy have been separately reviewed.

Before opening an issue, try the [troubleshooting cookbook](docs/troubleshooting/README.md).
Attach only a short sanitized excerpt, not full logs, maps, private XODR or
screenshots exposing machine paths. Security reports follow [SECURITY.md](SECURITY.md).

## Development checks

For behavior changes:

1. Add a characterization or failing test.
2. Make the smallest change.
3. Run `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider` from the documented Python 3.10 environment.
4. State the highest evidence level actually reached.
5. Add compatibility claims only with a redacted evidence bundle.

Do not convert `NOT_RUN` to `PASS`, invent version commands, bypass path guards,
or use host filesystem moves for Unreal assets.

Install development dependencies from the [installation guide](docs/installation.md).
Run `ruff check .` with the existing Ruff configuration, and
`python3 development/shared/release_tools/check_doc_links.py` for local document links.
Public additions require exact entries in `PUBLICATION_ALLOWLIST.json`.
The [development index](development/shared/README.md) separates design/history
from user docs; the [release checklist](docs/release/github-settings-checklist.md)
tracks metadata and publication steps. Do not advertise compatibility merely
because a report or screenshot was submitted.
