---
title: Define the public installation and distribution contract
label: wayfinder:research
mode: AFK
status: closed
assignee: codex
blocked_by: []
---

## Question

What single supported installation path, package shape, host-version contract
and five-minute quick start can be reproduced from a clean public clone without
private files or machine-specific paths?

## Resolution

Use the repository as one Codex marketplace and install the complete
`carla-map-migration-toolkit` Plugin. The single v0.1 path is a clean clone,
repository-local `.venv`, pinned runtime requirements, `codex plugin marketplace
add .`, and the `carla-map-migration-toolkit@carla-map-migration-toolkit`
selector through `codex plugin add`. Per-Skill copying, symlinks, PyPI and
automatic CARLA/Unreal installation are unsupported.

The first supported host contract is Ubuntu 22.04.5 x86_64, Codex CLI 0.148.0,
Python 3.10.12, Git 2.34.1, and `jsonschema==4.26.0`.
macOS, Windows, desktop, IDE and cloud installation remain `NOT_RUN`.

An isolated Codex 0.148.0 probe installed and listed the complete Plugin with
all three Skills, and fresh Python 3.10.12 and 3.13.11 virtual environments
installed the runtime dependency and started `cmtk.py --help`. Only 3.10.12 is
the release-host contract. The exact public URL, immutable release tag,
clean-clone replay and live Skill-to-venv binding remain for the existing
clean-clone acceptance ticket; they are not claimed here.

The canonical commands and proof boundary are in
[`docs/installation.md`](../../../../docs/installation.md), with primary-source
research in
[`codex-plugin-installation.md`](../../release-research/codex-plugin-installation.md).
