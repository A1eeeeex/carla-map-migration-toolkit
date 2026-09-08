# GitHub settings and release checklist

Observed on 2026-09-08: repository public, description present, Topics empty,
Discussions disabled, no tags or Releases. Remote main `1f39e62` had successful
CI run 34201162498 (442 host tests, engine job skipped). Recheck before publication.

The available connector exposes no repository-metadata or Release mutation
operation, and no authenticated management CLI is configured for this task.
No remote settings were changed. This is the manual fallback, not a completed setup.

## Description and Topics

In the repository About editor, use:

> Codex Plugin + CLI for CARLA custom-map migration: RoadRunner to Source CARLA, then Package CARLA or UE4.27, with audits and evidence-driven validation.

Suggested Topics (12, lowercase and hyphenated):

```text
carla carla-simulator roadrunner opendrive datasmith custom-map
unreal-engine autonomous-driving simulation codex-plugin map-migration xodr
```

- [ ] Save the description and selected Topics; verify them on the public page.
- [ ] Keep the website field empty until a real documentation site exists.

[GitHub's topic rules](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/classifying-your-repository-with-topics)
allow lowercase letters/numbers/hyphens, at most 50 characters per topic and 20 topics.

## Social preview

- [x] Render [social-preview.svg](../assets/social/social-preview.svg) to 1280×640 PNG.
- [x] Inspect text and cropping; the diagram contains no official logos or map imagery.
- [ ] Upload the PNG through repository Settings → Social preview.
- [ ] Verify a public link preview; a committed SVG alone does not set the preview.

The upload-ready PNG is a local handoff artifact, not part of the source release.
To regenerate it with ImageMagick in `shell-build` from the clone root:

```bash
preview_dir="$(mktemp -d -t cmtk-preview.XXXXXX)"
convert -background '#101b2b' docs/assets/social/social-preview.svg "$preview_dir/social-preview.png"
identify "$preview_dir/social-preview.png"
```

[GitHub's image requirements](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/customizing-your-repositorys-social-media-preview)
specify PNG/JPG/GIF below 1 MB; 1280×640 is the recommended display size.
Keep the generated PNG local for this upload. Public map media has a separate rights
and allowlist gate; this technical diagram is not real-map evidence.

## Community

- [ ] Decide whether to enable Discussions; optional and not a release blocker.
- [ ] Add Q&A, Show and tell, Compatibility and Ideas categories.
- [ ] Keep private disclosures on the process in [SECURITY.md](../../SECURITY.md);
  verify private vulnerability reporting separately before directing users there.
- [ ] Check the bug, compatibility and feature forms after their commit is public.

## Experimental prerelease

- [ ] Check Plugin manifest version is 0.1.0 and the changelog matches.
- [ ] Review and commit the candidate; do not tag a dirty working snapshot.
- [ ] Run full host tests, lint, Plugin structure, quickstart, links and public-source checks.
- [ ] Review the exact candidate's history and Actions evidence before tag/publication.
- [ ] Push only the intended branch after authorization and check its new CI result.
- [ ] Confirm `v0.1.0` does not already exist. Never move an existing public tag.
- [ ] Create `v0.1.0` on the reviewed commit and mark **Pre-release**.
- [ ] Title: **v0.1.0 — Experimental Public Preview**; mark **Pre-release**.
- [ ] Use [release notes](v0.1.0-release-notes.md). When pasting into GitHub's Release
  editor, resolve relative documentation links against the exact tagged source.
- [ ] Use GitHub's source download or a freshly allowlisted source archive from that
  exact commit. Do not reuse a stale pre-productization archive or upload map assets.

Preparation is not publication. Source gates do not imply a strict RC or L3–L5 acceptance.
The final handoff supplies the exact candidate SHA and its CI/audit results.
Do not substitute a later main commit without checking it.

## Backlog

1. Rights-cleared public Golden Map: execute selected routes, review evidence and capture media.
2. Standalone CLI/PyPI distribution, designed separately from Plugin-first v0.1.
3. CARLA 0.10 / UE5 workflow research and independent compatibility evidence.
4. Additional real map/Profile combinations and community reproduction.
5. Community promotion after a useful, reproducible Golden Map case is available.
