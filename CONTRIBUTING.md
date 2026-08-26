# Contributing

Contributions should stay within one of the three migration routes or their
shared safety/repair/validation core. Do not add private assets or binaries.

For behavior changes:

1. Add a characterization or failing test.
2. Make the smallest change.
3. Run `python3 -m pytest -q`.
4. State the highest evidence level actually reached.
5. Add compatibility claims only with a redacted evidence bundle.

Do not convert `NOT_RUN` to `PASS`, invent version commands, bypass path guards,
or use host filesystem moves for Unreal assets.
