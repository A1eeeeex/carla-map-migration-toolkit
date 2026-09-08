# Security policy

Do not attach maps, exports, XODR, Unreal assets, engine binaries, credentials,
environment files, internal paths, full logs, or customer identifiers to a public
report. Provide the smallest anonymous JSON/text fixture that reproduces a host
logic issue.

Treat migration inputs and package archives as untrusted. Run inspect/plan first,
keep allowed roots narrow, inspect archives before extraction, and use Unreal
APIs for assets.

For security issues, use GitHub's
[private vulnerability reporting form](https://github.com/A1eeeeex/carla-map-migration-toolkit/security/advisories/new).
Do not open a public issue containing sensitive details. If the private form is
not yet available, open only a minimal public issue asking `@A1eeeeex` to
establish a private channel.
