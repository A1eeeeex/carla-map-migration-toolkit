from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import yaml
from conftest import PLUGIN_ROOT, REPO_ROOT

INSTALLATION_DOC = REPO_ROOT / "docs" / "installation.md"
MARKETPLACE_PATH = REPO_ROOT / ".agents" / "plugins" / "marketplace.json"
RUNTIME_REQUIREMENTS = REPO_ROOT / "requirements-runtime.txt"
QUICKSTART = REPO_ROOT / "demo" / "quickstart" / "run_demo.py"
LOGIC_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "logic-tests.yml"


def test_repository_is_one_marketplace_for_the_complete_plugin():
    manifest = json.loads((PLUGIN_ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
    marketplace = json.loads(MARKETPLACE_PATH.read_text(encoding="utf-8"))

    assert INSTALLATION_DOC.is_file()
    assert marketplace["name"] == "carla-map-migration-toolkit"
    assert len(marketplace["plugins"]) == 1
    assert marketplace["plugins"][0]["name"] == manifest["name"] == "carla-map-migration-toolkit"
    assert (REPO_ROOT / marketplace["plugins"][0]["source"]["path"]).resolve() == PLUGIN_ROOT.resolve()
    assert {path.name for path in (PLUGIN_ROOT / "skills").iterdir() if path.is_dir()} == {
        "roadrunner-to-source-carla",
        "source-carla-to-package-carla",
        "source-carla-to-ue427",
    }


def test_declared_host_runtime_starts_from_a_standalone_plugin_copy(tmp_path: Path):
    runtime_requirements = RUNTIME_REQUIREMENTS.read_text(encoding="utf-8").splitlines()
    development_requirements = (REPO_ROOT / "requirements-dev.txt").read_text(encoding="utf-8").splitlines()

    assert runtime_requirements == ["jsonschema==4.26.0"]
    assert development_requirements == [
        "--requirement requirements-runtime.txt",
        "pytest==9.1.1",
        "PyYAML==6.0.3",
        "ruff==0.16.3",
    ]

    plugin_copy = tmp_path / "carla-map-migration-toolkit"
    shutil.copytree(PLUGIN_ROOT, plugin_copy)
    result = subprocess.run(
        [sys.executable, str(plugin_copy / "scripts" / "cmtk.py"), "--help"],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "Guarded host core for CARLA map migration evidence." in result.stdout


def test_installation_guide_has_one_versioned_five_minute_path():
    guide = INSTALLATION_DOC.read_text(encoding="utf-8")
    ignored_paths = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()

    assert "Ubuntu 22.04.5 LTS on x86_64" in guide
    assert "Codex CLI 0.153.4" in guide
    assert "Python 3.10.12" in guide
    assert "Git 2.34.1" in guide
    assert "python3.10 --version" in guide
    assert "codex --version" in guide
    assert "codex plugin --help" in guide
    assert "python3.10 -m venv .venv" in guide
    assert ".venv/bin/python -m pip install --requirement requirements-runtime.txt" in guide
    assert "codex plugin marketplace add ." in guide
    assert "codex plugin add carla-map-migration-toolkit@carla-map-migration-toolkit" in guide
    assert "codex plugin list --marketplace carla-map-migration-toolkit --json" in guide
    assert "CMTK_EXECUTION_CONTEXT=host-cpython .venv/bin/python" in guide
    assert "plugins/carla-map-migration-toolkit/scripts/cmtk.py --help" in guide
    assert '.venv/bin/python demo/quickstart/run_demo.py --workspace-root "$demo_root"' in guide
    assert QUICKSTART.is_file()
    assert "codex plugin install" not in guide
    assert ".venv/" in ignored_paths


def test_readmes_route_installation_to_the_canonical_contract():
    english = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    chinese = (REPO_ROOT / "README.zh-CN.md").read_text(encoding="utf-8")
    contributing = (REPO_ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")

    for readme in (english, chinese):
        assert "docs/installation.md" in readme
        assert "requirements-runtime.txt" in readme
        assert "codex plugin marketplace add ." in readme
        assert "codex plugin add carla-map-migration-toolkit@carla-map-migration-toolkit" in readme
        assert ".venv/bin/python -m pip install --requirement requirements-dev.txt" in readme
        assert "PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1" in readme
        assert ".venv/bin/python -m pytest -q -p no:cacheprovider" in readme
        assert "python3.10 -m pytest -q" not in readme
        for skill_name in (
            "roadrunner-to-source-carla",
            "source-carla-to-package-carla",
            "source-carla-to-ue427",
        ):
            assert f"$carla-map-migration-toolkit:{skill_name}" in readme
            assert f"Use ${skill_name}" not in readme
    assert "CMTK_EXECUTION_CONTEXT=host-cpython .venv/bin/python" in english
    assert "plugins/carla-map-migration-toolkit/scripts/cmtk.py inspect" in english
    assert "python3 plugins/carla-map-migration-toolkit/scripts/cmtk.py inspect" not in english
    assert "PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1" in contributing
    assert ".venv/bin/python -m pytest -q -p no:cacheprovider" in contributing

    guide = INSTALLATION_DOC.read_text(encoding="utf-8")
    assert "$carla-map-migration-toolkit:source-carla-to-ue427" in guide
    assert "Use $source-carla-to-ue427" not in guide


def test_all_skills_use_the_documented_clone_root_runtime_path():
    expected_cli = (
        "CMTK_EXECUTION_CONTEXT=host-cpython "
        ".venv/bin/python plugins/carla-map-migration-toolkit/scripts/cmtk.py"
    )
    for skill_path in sorted((PLUGIN_ROOT / "skills").glob("*/SKILL.md")):
        content = skill_path.read_text(encoding="utf-8")
        assert "docs/installation.md" in content
        assert expected_cli in content
        assert "../../scripts/cmtk.py" not in content


def test_hosted_logic_ci_preserves_the_publication_clean_tree_contract():
    workflow = yaml.safe_load(LOGIC_WORKFLOW.read_text(encoding="utf-8"))
    job = workflow["jobs"]["l0-l2"]

    assert job["env"] == {
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
    }
    assert job["steps"][-1]["run"] == "python -m pytest -q -p no:cacheprovider"
    assert job["steps"][-2] == {"name": "Ruff", "run": "python -m ruff check ."}
    requirements = (REPO_ROOT / "requirements-dev.txt").read_text()
    assert "ruff==0.16.3" in requirements.splitlines()
