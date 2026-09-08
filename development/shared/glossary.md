# CARLA Map Migration Toolkit

This context names the release and evidence concepts shared by the three map
migration routes.

## Language

**Migration Route**:
One of the three supported source-to-target transformations. A route is not a
version or import variant.
_Avoid_: Workflow, Profile

**Profile**:
A declared source or target variant within one Migration Route.
_Avoid_: Route, Mode

**Primary Profile**:
The Profile selected to prove a Migration Route for the first release
candidate. Other Profiles may remain explicitly experimental.
_Avoid_: Default Route, All Profiles

**Route Coverage**:
Evidence that every supported Migration Route has an accepted Verified Run for
its Primary Profile.
_Avoid_: One-route Proof, Profile Coverage

**Profile Coverage**:
The set of Profiles with accepted Verified Runs. Complete Profile Coverage is
not implied by complete Route Coverage.
_Avoid_: Route Coverage

**Historical Validation**:
A prior real execution that can characterize behavior but is not bound to the
current Toolkit commit and evidence contracts.
_Avoid_: Current Verified Run, Fixture Test

**Current-toolkit Verified Run**:
A real execution whose exact Toolkit commit, environment, stages, checks,
artifacts and hashes satisfy the current route acceptance contract.
_Avoid_: Historical Validation, Successful Command

**Rights-safe Replay Input**:
An original or explicitly authorized external map input whose binary content
remains outside the repository.
_Avoid_: Public Fixture, Customer Sample
