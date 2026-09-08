# Codex Plugin installation and distribution contract

Research date: 2026-08-28\
Execution context: `host-cpython`\
Scope: the single clean-clone path for this repository's skills-only Codex
Plugin. This note does not authorize publication or an OpenAI directory
submission.

## Decision

Use the repository itself as one Codex marketplace and distribute the complete
`carla-map-migration-toolkit` Plugin. For the first release, support one
automatable clean-clone path on the tested Linux host:

```bash
git clone --branch <RELEASE_TAG> <PUBLIC_REPOSITORY_URL> carla-map-migration-toolkit
cd carla-map-migration-toolkit
python3.10 -m venv .venv
.venv/bin/python -m pip install --requirement requirements-runtime.txt
codex plugin marketplace add .
codex plugin add carla-map-migration-toolkit@carla-map-migration-toolkit
codex plugin list --marketplace carla-map-migration-toolkit --json
CMTK_EXECUTION_CONTEXT=host-cpython .venv/bin/python \
  plugins/carla-map-migration-toolkit/scripts/cmtk.py --help
```

The release gate must replace both placeholders with the public URL and an
immutable release tag, then replay the sequence from a clean clone. Until that
happens, this is the selected contract, not a completed portability claim.

This choice follows OpenAI's documented repo-marketplace layout and its
documented `codex plugin marketplace add` source registration. Codex 0.148.0's
official source and local help define `codex plugin add` as installation from a
configured marketplace snapshot. [OpenAI's packaging guide](https://developers.openai.com/plugins/build/plugins#add-a-marketplace-from-the-cli),
[Codex 0.148.0 `plugin add` source](https://github.com/openai/codex/blob/rust-v0.148.0/codex-rs/cli/src/plugin_cmd.rs)

## Official facts

- A Plugin is the installable unit, must have `.codex-plugin/plugin.json`, and
  may bundle multiple related Skills. Local and repo marketplaces are separate
  authoring, testing, and team-distribution sources, not the universal public
  directory. [Plugin architecture](https://developers.openai.com/plugins/concepts/plugins),
  [package your plugin](https://developers.openai.com/plugins/build/plugins#package-and-distribute-plugins)
- A repo marketplace lives at `$REPO_ROOT/.agents/plugins/marketplace.json`;
  local `source.path` values are `./`-prefixed, relative to the marketplace
  root, and remain inside that root. [Marketplace metadata](https://developers.openai.com/plugins/build/plugins#marketplace-metadata)
- `codex plugin marketplace add` accepts a local directory, GitHub
  `owner/repo`, HTTP(S)/SSH Git URLs, and an optional pinned Git ref. The
  official 0.148.0 implementation also exposes the corresponding local/Git
  subcommand. [OpenAI packaging guide](https://developers.openai.com/plugins/build/plugins#add-a-marketplace-from-the-cli),
  [Codex 0.148.0 marketplace source](https://github.com/openai/codex/blob/rust-v0.148.0/codex-rs/cli/src/marketplace_cmd.rs)
- Codex 0.148.0 exposes `plugin add`, `list`, `marketplace`, and `remove`.
  `plugin add PLUGIN@MARKETPLACE` installs from a configured marketplace
  snapshot. There is no `plugin install`, `plugin update`, or `plugin
  uninstall` subcommand in that release. [Codex 0.148.0 `plugin` source](https://github.com/openai/codex/blob/rust-v0.148.0/codex-rs/cli/src/plugin_cmd.rs)
- A Git-backed marketplace invokes the host `git` executable. OpenAI's source
  does not declare a minimum Git version. [Codex 0.148.0 Git install path](https://github.com/openai/codex/blob/rust-v0.148.0/codex-rs/core-plugins/src/marketplace_add/install.rs)
- Direct copying is documented only as a way to place a plugin under a repo or
  personal marketplace; the marketplace metadata is still part of discovery.
  Skill symlinks are ignored by public submission validation. [Manual local
  install](https://developers.openai.com/plugins/build/plugins#install-a-local-plugin-manually),
  [submission errors](https://developers.openai.com/plugins/deploy/submission-errors#package-warnings)
- Publishing to the universal Plugins Directory is a separate OpenAI Platform
  review flow. A public Git repository or repo marketplace alone is not that
  publication. Skills-only Plugins are eligible for submission. [Submit
  plugins](https://developers.openai.com/plugins/deploy/submission)

## Observed repository and host facts

- The current repository has one marketplace named
  `carla-map-migration-toolkit`; it points to one complete Plugin through
  `./plugins/carla-map-migration-toolkit`. The Plugin manifest declares version
  `0.1.0`, `skills: "./skills/"`, and the three route Skill directories are
  present. [Marketplace catalog](../../../.agents/plugins/marketplace.json),
  [Plugin manifest](../../../plugins/carla-map-migration-toolkit/.codex-plugin/plugin.json)
- The deterministic CLI is a source-tree script, not a PyPI package: there is
  no `[project]`, `requires-python`, or console entry point in
  [`pyproject.toml`](../../../pyproject.toml).
- Current Python source uses Python 3.10-only language/library features,
  including `X | None` annotations and `zip(..., strict=True)`, while Ruff
  targets `py310`. Therefore Python 3.10 is the lowest version supported by
  repository evidence, even though it is not yet declared as package metadata.
- The host core imports `jsonschema`; the current runtime contract pins
  `jsonschema==4.26.0`. No CARLA, Unreal, RoadRunner, or private binary is a host
  CLI dependency. [Runtime requirements](../../../requirements-runtime.txt),
  [plan validator](../../../plugins/carla-map-migration-toolkit/scripts/cmtk/core/plans.py)
- Reference host observed for this research: Ubuntu 22.04 x86_64, Codex CLI
  0.148.0, Git 2.34.1, system Python 3.10.12, active Python 3.13.11, and
  jsonschema 4.26.0.
- An isolated, non-global probe on Codex CLI 0.148.0 passed
  `marketplace add .`, `plugin add`, installed/enabled listing, manifest
  presence, and presence of all three bundled Skills. The probe used the
  current worktree and a temporary Codex configuration directory; it did not
  test a public remote, a clean clone, another machine, or a live migration.
- A separate fresh virtual environment created with Ubuntu's Python 3.10.12
  installed `requirements-runtime.txt` and started `cmtk.py --help`. The same
  dependency/startup probe also passed under Python 3.13.11, but only 3.10.12
  belongs to the first release-host contract.

## Inferences and supported-version contract

The following are release decisions derived from the facts above, not upstream
minimum-version guarantees:

| Component | v0.1 contract | Basis |
|---|---|---|
| Codex CLI | `0.148.0` | Exact release observed and source-pinned; other releases are unverified. |
| Python | `3.10.12` | Exact Ubuntu release-host interpreter tested in a fresh virtual environment; 3.13.11 remains development evidence only. |
| Python runtime dependency | `jsonschema==4.26.0` | Direct import plus repository runtime requirements. |
| Git for the CMTK CLI | Not required at runtime | No Plugin host-core module invokes Git. |
| Git for clone/Git marketplace distribution | `2.34.1` | Exact host version observed; neither this repo nor upstream establishes a range. |
| Supported OS for the first clean-clone claim | Ubuntu 22.04.5 x86_64 | Only current reproducible reference host; other hosts remain unverified. |

Pinning the release tag matters: `marketplace add owner/repo --ref <tag>` can
materialize a versioned Git snapshot, whereas direct copy/symlink instructions
create unmanaged drift. The local-clone form (`marketplace add .`) is retained
as the first acceptance path because it also gives users the runtime
requirements and deterministic CLI files that a bare marketplace install does
not provision into a Python environment.

## Rejected alternatives

| Alternative | Decision | Reason |
|---|---|---|
| `codex plugin install ...` | Reject | No such 0.148.0 subcommand; publishing it would be an invented command. |
| Install one Skill directory | Reject | The three Skills share Plugin-level scripts, schemas, profiles, references, and templates. |
| Copy into a global Skills directory | Reject | Bypasses the Plugin manifest and marketplace identity; not the product's package unit. |
| Symlink the Plugin or Skills | Reject | No public compatibility guarantee for a Plugin symlink, and public submission explicitly ignores Skill symlinks. |
| PyPI / console-script install | Reject for v0.1 | The repository is not a Python distribution and declares no console entry point. |
| OpenAI universal directory | Later release channel | Requires a separate submission/review and identity/policy attestations; it is not a substitute for the Git clean-clone gate. |

## Unknowns and remaining release evidence

- **NOT_RUN:** the exact sequence above from an unauthenticated clean public
  clone at an immutable tag.
- **NOT_RUN:** a clean machine or container proving the Plugin cache, three
  Skills, Python dependency setup, `cmtk.py --help`, tests, and example dry run.
- **Unknown:** which other Codex CLI releases support the complete
  marketplace/add behavior. Keep `0.148.0` as the supported release until a
  version matrix is run.
- **Unknown:** the minimum Git version accepted by Codex marketplace cloning.
  Git 2.34.1 is observed, not an upstream minimum.
- **Gap:** OpenAI's current user-facing packaging page documents marketplace
  registration but directs local UI installation/testing to the ChatGPT desktop
  app; `codex plugin add` is evidenced by the 0.148.0 binary and official source,
  not yet by that user-facing page.
- **Partially closed:** marketplace installation does not itself create the
  repository `.venv` or install `jsonschema`, so the documented clean-clone
  bootstrap remains required. All three Skill command examples now resolve
  `.venv/bin/python` from the repository root, and that path passed the
  allowlisted snapshot rehearsal. Three independent ephemeral sessions also
  selected the correct Plugin-qualified Skill for one canonical route prompt
  each. The immutable-tag clean-clone must repeat both installation and
  discovery before claiming hands-off installation.
- **Gap:** no current evidence proves availability or identical behavior in the
  ChatGPT desktop app, Codex IDE, Codex cloud, Windows, or macOS.

These unknowns prevent an L5 portability claim; they do not invalidate the
isolated local Codex 0.148.0 installation probe.
