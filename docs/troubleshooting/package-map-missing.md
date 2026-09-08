# Custom map is missing from Package CARLA or the archive layout is wrong

## Symptoms

The map is absent from available maps, loads empty, or loses materials only after CARLA map packaging.

## What usually needs checking

Trace saved Source assets to Package JSON, MapsToCook, Cook reachability, staged XODR, archive members, target installation and actual server. Match build/target OS, architecture and CARLA version.

## Toolkit diagnosis

From the installed clone in host-cpython; replace every angle-bracket value
with your own permitted local input before running:

```bash
CMTK_EXECUTION_CONTEXT=host-cpython .venv/bin/python plugins/carla-map-migration-toolkit/scripts/cmtk.py map-package-audit --target <archive-or-staging-tree> --allowed-root <input-root> --map-name ExampleMap
CMTK_EXECUTION_CONTEXT=host-cpython .venv/bin/python plugins/carla-map-migration-toolkit/scripts/cmtk.py archive-audit --archive <package.tar.gz> --allowed-root <input-root> --require '*.umap' --require '*.xodr'
```

The named-map audit checks an unambiguous ExampleMap and matching XODR. DELIVERY-CONTENT-INCOMPLETE signals missing/wrong members; PKG-ARCHIVE-UNSAFE-LINK or PKG-ARCHIVE-UNSAFE-TRAVERSAL blocks unsafe input. DELIVERY-ASSET-CATEGORIES-UNCONFIRMED is a WARN about folder hints, not proof of missing binary dependencies. Add --require-cooked-sidecars only for a profile known to require a map .uexp.

## Manual / Editor checkpoint

Inspect version-specific Cook logs and Asset Registry in Source. Resolve actual build/import commands from that checkout in shell-build; back up before target replacement. Do not copy a lone .umap into a binary installation or extract an unsafe archive.

## Validation

Audit the rebuilt archive, verify install/hash identity, then independently load the named map with a matching carla-client-python. Check views, collision, XODR/spawn and bounded driving in the target installation.

## Evidence to keep

Package configuration summary, Cook findings, archive audit/hash, target identity, map registration/load observations and runtime checks. Full logs and private assets stay local.

## What this guide does NOT prove

Archive structure and matching names do not prove successful Cook, dependency closure, runtime load or portability. The generic archive audit is not a substitute for the named-map check.

Based on the repository's [operation reference](../../plugins/carla-map-migration-toolkit/references/carla-map-operations.md),
[reason codes](../../plugins/carla-map-migration-toolkit/references/reason-codes.md)
and existing host/fixture checks. [Back to cookbook](README.md).
