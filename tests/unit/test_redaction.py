from cmtk.core.redaction import redact_text


def test_redaction_removes_user_paths_network_and_email():
    source = "owner@example.invalid /home/demo/private/map 192.0.2.24 token=secret-value"
    result = redact_text(source)
    assert "owner@example.invalid" not in result
    assert "/home/demo/private/map" not in result
    assert "192.0.2.24" not in result
    assert "secret-value" not in result
    assert "[REDACTED_EMAIL]" in result
    assert "[REDACTED_LOCAL_PATH]" in result


def test_redaction_removes_unreal_asset_and_mount_paths():
    source = "/Game/PrivateMap/PrivateMap /mnt/internal/maps /opt/internal/source"
    result = redact_text(source)
    assert "PrivateMap" not in result
    assert "/mnt/" not in result
    assert "/opt/" not in result
    assert "[REDACTED_ASSET_PATH]" in result


def test_redaction_removes_caller_supplied_customer_and_map_identifiers():
    result = redact_text(
        "ProjectOrchid uses map ORCHID_DOWNTOWN for CustomerNimbus.",
        sensitive_terms=["ProjectOrchid", "orchid_downtown", "CustomerNimbus"],
    )
    assert "orchid" not in result.lower()
    assert "nimbus" not in result.lower()
    assert result.count("[REDACTED_IDENTIFIER]") == 3
