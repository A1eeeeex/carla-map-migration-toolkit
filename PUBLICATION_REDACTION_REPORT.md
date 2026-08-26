# Publication redaction report

Date: 2026-08-26

## Scope

The candidate publication allowlist is limited to `plugins/`, `tests/`, `evals/`,
`docs/`, `development/shared/`, `.agents/plugins/`, `.github/workflows/`, the
root README and policy files, and the root implementation/verification reports.
Original handoff prompts, discovery records, drafts, private inputs, mounted
external environments, full logs, and historical evidence are consolidated
under the Git-ignored `development/local/` tree and are not publication
candidates.

`PUBLICATION_ALLOWLIST.json` enumerates every candidate file. Its integration
test rejects unlisted files under the candidate roots, forbidden binary/asset
suffixes, common host paths, secret assignments, and configured private
identifiers. Synthetic redaction-test literals are the only content-scan
exceptions and are named explicitly in that manifest.

## Results

- No customer or legacy map identifier was found in the candidate allowlist.
- No real local host/mount path was found in the candidate allowlist.
- No candidate file has an Unreal/map/export extension such as `.uasset`,
  `.umap`, `.uexp`, `.ubulk`, `.fbx`, `.udatasmith`, or `.xodr`.
- No CARLA/Unreal/RoadRunner binary or private asset was copied.
- No credentials were found. The only credential-like strings are synthetic
  values inside the redaction unit test.
- The only email/network-like values are the reserved `.invalid` email and the
  documentation-only `192.0.2.0/24` address used to test redaction.
- Policy documents contain generic words such as “customer” to state prohibited
  content; these are not identifiers.
- Legacy source code remains `copied_into_candidate: false` in the source
  inventory because publication rights are unknown.
- The redaction helper supports an explicit caller-supplied set of private
  customer, project, and map identifiers. Publication tooling must supply that
  known set; generic patterns cannot safely infer arbitrary names.
- The final exact-file allowlist, suffix, host-path, and secret-assignment gates
  passed as part of the `220 passed` full suite after generated caches were
  removed.

## Required pre-publication actions

1. Select a license and verified copyright/maintainer identity.
2. Populate `prohibited_literals` from the private source register outside the
   candidate, then re-run the exact-file allowlist scan.
3. Obtain explicit redistribution rights for any demo media or evidence bundle.
4. Run model trigger evals and authorized real route replays; publish only
   redacted summaries/manifests.
5. Perform a clean-clone installation check in the intended Codex host.

A private GitHub repository was created and `main` was pushed only after explicit
user authorization. The repository remains `PRIVATE`; `development/local/` was
excluded by Git, and no public release, asset upload, or visibility change was
performed.
