# Release publication audit

`publication_audit.py` is a fail-closed, `host-cpython` pre-publication gate. It
checks a clean release-candidate worktree, every locally reachable Git object
and ref, and an unpacked private GitHub Actions export against an approved
private literal set. It also rejects forbidden map/archive/log suffixes in the
current or historical public tree and binary blobs that cannot be completely
text-scanned. Reports contain counts and SHA-256 subject fingerprints; they do
not echo private literals, paths or matching content.

## Inputs

- `--repo`: the clean Git release candidate.
- `--private-literals`: a UTF-8 file with one approved private customer,
  project, map, host or credential literal per line. Blank lines and lines
  beginning with `#` are ignored. Keep this file outside the publication
  candidate and do not commit it.
- `--external-root`: a complete, safely unpacked export of all private Actions
  logs and artifact text in scope. The directory must exist, contain at least
  one regular file and contain no symbolic links. Keep it outside Git.

Run from the repository root:

```shell
python3 development/shared/release_tools/publication_audit.py \
  --repo . \
  --private-literals <private-literals.txt> \
  --external-root <actions-export-directory>
```

Exit code `0` means `PASS`. Exit code `2` means `FAIL` or `BLOCKED`. A match is
reported as `PUBLICATION-PRIVATE-LITERAL-DETECTED`. Empty or missing inputs, an
unsafe export, or a dirty worktree produce stable `PUBLICATION-*` blocker codes
instead of a pass. Any individual scan input over 64 MiB is blocked for separate
handling rather than loaded without a bound. Forbidden public paths and binary
content use `PUBLICATION-FORBIDDEN-ASSET-PATH` and
`PUBLICATION-BINARY-CONTENT-DETECTED` respectively. Binary Actions artifacts
must be safely unpacked or converted to reviewed UTF-8 text before this gate.

## Proof boundary

The tool does not determine whether the private literal set is authoritative,
whether the Actions export is complete, or whether GitHub has refs that are not
present in the local repository. Those inputs require separate approval,
authenticated export evidence and an authenticated full-ref mirror. Until all
three exist, a real publication audit is `NOT_RUN` or `BLOCKED`; a fixture-only
pass is not release evidence.

Treat the complete JSON report as private working evidence. Its deterministic
fingerprints can be dictionary-enumerated when source names have low entropy.
Do not commit or publish the report; derive a separately reviewed aggregate
release statement after the audit passes.
