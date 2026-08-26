from cmtk.routes.inspection import inspect_workspace


def test_valid_anonymous_workspace_passes_host_inspection(workspace_factory):
    workspace = workspace_factory("roadrunner-to-source-carla")
    result = inspect_workspace(workspace, "roadrunner-to-source-carla")
    assert result["status"] == "PASS"
    assert result["execution_context"] == "host-cpython"


def test_package_platform_mismatch_is_blocked(workspace_factory):
    workspace = workspace_factory("source-carla-to-package-carla")
    workspace["package_carla"]["platform"] = "windows-x86_64"
    result = inspect_workspace(workspace, "source-carla-to-package-carla")
    assert result["status"] == "BLOCKED"
    assert any(check.get("reason_code") == "PKG-TARGET-PLATFORM-MISMATCH" for check in result["checks"])


def test_unknown_roadrunner_profile_is_blocked(workspace_factory):
    workspace = workspace_factory("roadrunner-to-source-carla")
    workspace["input"]["profile"] = "unknown-export"
    result = inspect_workspace(workspace, "roadrunner-to-source-carla")
    assert result["status"] == "BLOCKED"
    assert any(check.get("reason_code") == "RR-INPUT-PROFILE-UNKNOWN" for check in result["checks"])


def test_package_version_mismatch_is_blocked(workspace_factory):
    workspace = workspace_factory("source-carla-to-package-carla")
    workspace["package_carla"]["version"] = "0.9.15"
    result = inspect_workspace(workspace, "source-carla-to-package-carla")
    assert result["status"] == "BLOCKED"
    assert any(check.get("reason_code") == "PKG-TARGET-VERSION-MISMATCH" for check in result["checks"])


def test_non_427_target_engine_is_blocked(workspace_factory):
    workspace = workspace_factory("source-carla-to-ue427")
    workspace["ue427"]["engine_version"] = "5.3.2"
    result = inspect_workspace(workspace, "source-carla-to-ue427")
    assert result["status"] == "BLOCKED"
    assert any(check.get("reason_code") == "UE427-ENGINE-VERSION-MISMATCH" for check in result["checks"])


def test_downstream_source_manifest_must_stay_under_source_input_root(workspace_factory):
    route = "source-carla-to-package-carla"
    workspace = workspace_factory(route)
    workspace["input"]["handoff_path"] = workspace["source_carla"]["xodr_path"]
    result = inspect_workspace(workspace, route)
    reason_codes = {item.get("reason_code") for item in result["checks"]}
    assert result["status"] == "BLOCKED"
    assert "PATH-OUTSIDE-ALLOWED-ROOT" in reason_codes


def test_downstream_source_manifest_fields_are_required(workspace_factory):
    route = "source-carla-to-ue427"
    workspace = workspace_factory(route)
    workspace["input"]["dependency_manifest_path"] = ""
    result = inspect_workspace(workspace, route)
    reason_codes = {item.get("reason_code") for item in result["checks"]}
    assert result["status"] == "BLOCKED"
    assert "SOURCE-INPUT-MANIFEST-INCOMPLETE" in reason_codes
