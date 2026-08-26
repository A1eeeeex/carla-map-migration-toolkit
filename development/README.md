# Development materials

Keep project-development material under this directory so the repository root
stays focused on the installable Plugin and its public contracts.

## Layout

- `shared/`: publication-safe proposals, design notes, implementation plans, and
  review records that should be versioned with the repository.
- `local/`: original handoff bundles, discovery evidence, drafts, private input,
  and machine-specific notes. This directory is intentionally ignored by Git.

Existing handoff material was moved into `local/` without changing its contents:

```text
local/
  analysis/
  drafts/
  examples/
  handoff/
  private-input/
  specs/
```

Do not place customer maps, private XODR, Unreal/CARLA binaries, engine assets,
credentials, or full private logs anywhere intended for a commit. Store such
inputs outside the repository or below `local/`, and publish only reviewed,
anonymous summaries.
