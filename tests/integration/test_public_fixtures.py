from conftest import REPO_ROOT

EXPECTED = {
    "source-carla-valid",
    "source-carla-map-missing",
    "source-carla-xodr-mismatch",
    "package-carla-valid",
    "package-json-invalid",
    "archive-path-traversal",
    "archive-map-not-cooked",
    "ue427-external-ref-summary",
    "performance-comparable",
    "performance-not-comparable",
}
FORBIDDEN_SUFFIXES = {".uasset", ".umap", ".uexp", ".ubulk", ".fbx", ".udatasmith", ".xodr"}


def test_public_fixture_catalog_is_anonymous_text_only():
    root = REPO_ROOT / "tests" / "fixtures"
    assert {path.name for path in root.iterdir() if path.is_dir()} == EXPECTED
    files = [path for path in root.rglob("*") if path.is_file()]
    assert files
    assert not any(path.suffix.lower() in FORBIDDEN_SUFFIXES for path in files)
    combined = "\n".join(path.read_text(encoding="utf-8") for path in files)
    assert "/home/" not in combined
    assert "token=" not in combined.lower()
