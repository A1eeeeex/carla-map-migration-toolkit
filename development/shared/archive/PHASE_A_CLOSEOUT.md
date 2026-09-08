# Phase A Closeout

> Archived development record. Statements and repository-root paths below describe
> the recorded period, not current release status. See [current status](../../../docs/current-status.md).

## 1. Executive Status

```text
Overall: INCOMPLETE
Source→UE4.27: L2 inspect/plan slice implemented; apply/repair/validate/cold-copy incomplete
Evidence level reached: L2 fixture
Maintainer-verified created: no
Next route allowed: no
```

## 2. Environment

- Host OS: Ubuntu 22.04, Linux x86_64.
- Source CARLA version/branch/commit: historical observed `0.9.16-dirty`, commit
  `294096eb1c38eabf246e4f3a9cdab704e33a7f4c`; no active route workspace.
- Source UE: historical observed CARLA fork 4.26.2.
- Target UE4.27: historical observed vanilla 4.27.2; no authorized active target.
- Python contexts: host CPython executed; Source Unreal, UE4.27 Unreal, CARLA
  client and shell-build contexts `NOT_RUN`.
- Map profile: `standalone-map` contract; no customer map copied or executed.
- Toolkit baseline: work began at Git commit `10c4da6`.
- Missing environment: active `map-workspace.json`, accepted Source handoff,
  authorized target project, second clean UE4.27 project, exact RoadRunner stack.

## 3. Source Discovery

- Found sources: legacy packaging Skill, 17 Python scripts and one performance report.
- Missing sources: active workspace/handoff.
- Script count: 17, 2,804 lines; hashes revalidated with no drift.
- Rights status: `RIGHTS_UNKNOWN` for every legacy source.
- Private/hardcoded findings: project identifiers, local/asset paths, Actor
  labels, camera poses, thresholds and mutation calls remain private.
- Inventory artifacts: `development/local/analysis/` (Git-ignored), including
  discovery report, source/script inventories, migration matrix, hardcode scan,
  rights assessment, baseline index, gap report and open questions.

## 4. Behavior Baseline

- live: 0.
- historical: 2 aggregate records (route behavior and performance).
- fixture: 0 legacy baselines; current-toolkit anonymous fixture tests are separate.
- unavailable: 0 discovered source classes; current live replay unavailable.
- key old behaviors preserved: Unreal-only asset moves, material/reference/
  environment/collision separation, clean-project acceptance, protected-property
  performance comparison.
- differences: private equality counts and camera/threshold constants are not
  promoted to public acceptance rules; current-toolkit replay remains `NOT_RUN`.

## 5. Claims Status

| Claim | Before | After | Evidence | Notes |
|---|---|---|---|---|
| C-PLUGIN-001 | implicit L0 | implemented | structure tests | no runtime claim |
| C-ROUTE-001 | implicit L1/L2 | implemented | static eval datasets | model eval not run |
| C-SAFE-001 | implicit L1/L2 | implemented | safety/plan/backup tests | Unreal rollback not run |
| C-EVID-001 | undocumented | experimental | schemas/status tests | real stages not run |
| C-SRC-UE427-001 | unverified | planned | L2 inspect/plan only | L3-L5 required |
| C-SRC-PKG-001 | unverified | planned | no real run | gated |
| C-RR-SRC-001 | unverified | planned | no real run | exact RR stack unknown |
| C-PERF-001 | historical only | experimental | L2 logic + historical summary | live comparable replay not run |

## 6. Implementation

### Core

Added Claims Registry and Verified Run contracts, cross-record traceability
validation and required-check aggregation. Sparse PASS records cannot satisfy
any route acceptance contract. Breaking plan/evidence contracts are versioned
through route-plan 1.5.0, Verified Run 1.4.0, check-evidence 1.1.0 and
redaction-report 1.1.0 with regeneration notes. Verified evidence now binds
checks to catalog stages, proof-capable evidence types and positive acceptance
observations, rehashes inputs, rejects non-relative paths, and verifies exact
redaction coverage from a single byte snapshot. Plans bind catalog safety
metadata and exact workspace read/write/backup paths.

### Source inspect/plan

Added Source→UE4.27 dependency classification with exactly six classes:
`portable`, `localizable`, `replaceable`, `remove`, `blocked`, `unknown`. Each
entry retains source object, target strategy, referencers, migration action,
verification, rollback and residual risk. Unknown, blocked, duplicate or
incomplete actions block inspection/planning; an empty dependency manifest is
also blocked as an incomplete fact source. Dependency actions and their
fingerprint are generated from the same in-memory file snapshot.

### Migration

`NOT_RUN`; no Unreal migration adapter or asset operation was executed.

### Repairs

`NOT_RUN`; material, reference, environment and collision repair adapters remain
future WP-A6 work.

### Validation

Verified Run schema, cross-record reference validation and route-status
aggregation are implemented at L1/L2.
Target Editor reopen and PIE are `NOT_RUN`.

### Cold-copy

`NOT_RUN`; no second UE4.27 project was created or populated.

## 7. Changed Files

- Claims/evidence docs: `docs/claims.md`, `docs/non-claims.md`,
  `docs/support-status.md`, `docs/acceptance-contracts.md`,
  `docs/proof-model.md`, `docs/claim-test-traceability.md`,
  `docs/current-status.md`, `evidence/**`.
- Contracts/examples: Claims Registry, Verified Run and compatibility matrix;
  route-plan assets now allow structured dependency actions.
- Host code: `routes/source_to_ue427.py`, route inspection/planning integration,
  and `validation/verified.py`.
- Fixtures/tests: anonymous dependency fixtures, claim/evidence tests, verified
  aggregation tests and Golden Map manifest test.
- Planning/status: `demo/golden-map/**`, `README.md`, `CHANGELOG.md`,
  `PUBLICATION_ALLOWLIST.json`, `PHASE_A_CLOSEOUT.md`.
- Local-only: updated `development/local/analysis/**` and timestamped backups;
  these are ignored and excluded from publication.

## 8. Validation Results

| Check | Status | Level | Evidence |
|---|---|---:|---|
| cumulative archive safety | PASS | L1 | 57 members; no findings |
| cumulative manifests | PASS | L1 | root/prior/Phase A SHA-256 checks |
| route/plan/schema/claim subset | PASS | L1/L2 | 80 passed |
| full pytest | PASS | L0-L2 | 302 passed |
| Ruff | PASS | L1 | all checks passed |
| Source/UE4.27 Editor | NOT_RUN | L3 | no authorized active workspace |
| UE4.27 PIE/collision | NOT_RUN | L4 | no authorized active target |
| second-project cold-copy | NOT_RUN | L5 | no authorized second project |

## 9. Verified Run

- run ID: none.
- status: `INCOMPLETE` example only.
- evidence path: `plugins/carla-map-migration-toolkit/examples/verified-run.example.json`.
- evidence hash: `c151d4339629d2748bb9d8c154f59f0a1f6fc3cbdc4e34fab2c384903f144e43` (incomplete example only).
- exact supported stack: none.
- limitations: L3-L5 are `NOT_RUN`; historical private evidence is not a
  current-toolkit verified run.

## 10. Golden Map

- lite status: plan-only; no map content exists.
- full status: private maintainer tier not assembled.
- rights: `REVIEW_REQUIRED`.
- variants: GM-F01 through GM-F08 defined with expected reason/status.
- public artifacts: text-only README and JSON manifest.

## 11. Safety and Rollback

- plans: dependency actions are sealed into the route plan; blockers prevent
  `verify-plan` success.
- backups: `development/local/backups/phase-a-20260826T074833Z/` contains copies
  and hashes of replaced local/public inputs.
- rollback test: repository-level diff is reviewable from `10c4da6`; no external
  rollback was necessary or executed.
- destructive actions: none.
- residual safety risk: Unreal apply/repair/rollback adapters are absent and must
  not be inferred from host-only tests.

## 12. Blockers and Open Questions

### UE427-ASSET-API-UNAVAILABLE

- impact: WP-A6 migration/repair cannot execute in host CPython.
- evidence: no active Source Unreal/UE4.27 job or workspace was supplied.
- next executable action: create an authorized workspace, then run
  `python3 plugins/carla-map-migration-toolkit/scripts/cmtk.py inspect --route source-carla-to-ue427 --config <map-workspace.json>`.
- blocks Verified: yes.

### UE427-TARGET-PROJECT-INVALID

- impact: target reopen, PIE and material/reference/environment/collision audits
  cannot run.
- evidence: no authorized active target `.uproject` is in the task workspace.
- next executable action: record exact target and backup roots in the authorized
  workspace and regenerate the sealed plan.
- blocks Verified: yes.

### UE427-COLD-COPY-FAILED

- impact: L5 portability cannot be assessed; this code is used as the route gate,
  not as a claim that an attempted copy failed.
- evidence: cold-copy `NOT_RUN`.
- next executable action: after primary target L3/L4 passes, create a genuinely
  separate vanilla UE4.27 project and copy only the handoff manifest contents via
  an approved Unreal workflow.
- blocks Verified: yes.

## 13. Next Recommendation

`REPAIR_PHASE_A`

Implement and replay WP-A5 Source Unreal exporters, then WP-A6 Unreal-safe
migration/repairs and WP-A7 target/cold-copy validation. Do not begin full
Source→Package implementation until L5 and user review pass.

## 14. Prohibited Claims

- Three verified migration workflows.
- Production-ready or one-click migration.
- Universal CARLA/RoadRunner/Unreal compatibility.
- Source→UE4.27 works on a real stack.
- Disallowed references, black materials or collision are fixed in a real map.
- Cold-copy or maintainer verification has passed.
- Historical private evidence proves the current implementation.
