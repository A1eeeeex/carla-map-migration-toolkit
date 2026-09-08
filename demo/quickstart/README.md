# Engine-free script example

This runnable script example proves that the host-side Toolkit can inspect an anonymous
RoadRunner-shaped input, seal a read-only migration plan, detect plan changes,
and stop honestly when real Editor/runtime evidence is absent.

It does **not** run RoadRunner, Unreal Editor or CARLA, and it does not prove a
map import. The generated Datasmith-shaped and OpenDRIVE text files are original
synthetic placeholders used only for L1 host-logic behavior. They are created
inside the supplied temporary directory and are never added to this repository.

From the repository root, after installing `requirements-runtime.txt`:

```bash
demo_root="$(mktemp -d -t cmtk-quickstart.XXXXXX)"
.venv/bin/python demo/quickstart/run_demo.py --workspace-root "$demo_root"
```

The script accepts only an absolute, empty, non-symlink workspace outside the
repository and home directory. A successful run reports:

- `inspection_status: PASS`;
- an unblocked, SHA-256-sealed plan;
- `plan_verification_status: PASS`; and
- `route_validation_status: NOT_RUN` as the expected safe stop, because no real
  Source CARLA Editor work has occurred.

The generated `map-workspace.json`, plan and pending validation report remain in
the temporary workspace for inspection. Remove that disposable directory when
you no longer need it.
