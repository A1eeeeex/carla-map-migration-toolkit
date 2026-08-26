# Safety guardrails

- Inventory before migration; baseline before optimization; plan before write.
- Resolve every path canonically and require containment within explicit roots.
- Reject empty paths, `/`, `~`, unresolved variables, broad targets, and roots
  outside the workspace allowlist.
- Recheck workspace and plan hashes immediately before any apply action.
- Back up every replaced target with a unique timestamped manifest.
- Never run `git clean`, `git reset --hard`, or recursive workspace deletion.
- Inspect tar/zip paths, traversal, links, duplicates, required members, and
  declared expansion size before extraction.
- Never move, rename, delete, consolidate, or back up Unreal binary assets with
  host OS file operations. Use AssetTools, EditorAssetLibrary, Asset Registry,
  Migrate, redirector repair, or a version-appropriate engine workflow.
- Query referencers before delete or replacement.
- Redact email, credentials, host paths, network addresses, customer/map names,
  and private asset locations from public evidence.
- Supply the known private customer, project, and map identifier set to the
  redaction helper; pattern-only redaction cannot discover arbitrary names.
