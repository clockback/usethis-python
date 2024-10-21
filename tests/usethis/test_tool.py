import subprocess
from pathlib import Path

import pytest

from usethis._pre_commit.core import _VALIDATEPYPROJECT_VERSION
from usethis._pre_commit.hooks import (
    _HOOK_ORDER,
    get_hook_names,
)
from usethis._test import change_cwd
from usethis._tool import ALL_TOOLS, get_dev_deps
from usethis.tool import _deptry, _pre_commit, _ruff


class TestToolPreCommit:
    def test_dependency_added(self, uv_init_dir: Path):
        # Act
        with change_cwd(uv_init_dir):
            _pre_commit()

        # Assert
        (dev_dep,) = get_dev_deps(uv_init_dir)
        assert dev_dep == "pre-commit"

    def test_stdout(self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]):
        # Act
        with change_cwd(uv_init_dir):
            _pre_commit()

        # Assert
        out, _ = capfd.readouterr()
        assert out == (
            "✔ Adding 'pre-commit' as a development dependency.\n"
            "✔ Writing '.pre-commit-config.yaml'.\n"
            "✔ Ensuring pre-commit hooks are installed.\n"
            "☐ Call the 'pre-commit run --all-files' command to run the hooks manually.\n"
        )

    def test_config_file_exists(self, uv_init_dir: Path):
        # Act
        with change_cwd(uv_init_dir):
            _pre_commit()

        # Assert
        assert (uv_init_dir / ".pre-commit-config.yaml").exists()

    def test_config_file_contents(self, uv_init_dir: Path):
        # Act
        with change_cwd(uv_init_dir):
            _pre_commit()

        # Assert
        contents = (uv_init_dir / ".pre-commit-config.yaml").read_text()
        assert contents == (
            f"""
repos:
  - repo: https://github.com/abravalheri/validate-pyproject
    rev: "{_VALIDATEPYPROJECT_VERSION}"
    hooks:
      - id: validate-pyproject
        additional_dependencies: ["validate-pyproject-schema-store[all]"]
"""
        )

    def test_already_exists(self, uv_init_repo_dir: Path):
        # Arrange
        (uv_init_repo_dir / ".pre-commit-config.yaml").write_text(
            """
repos:
  - repo: foo
    hooks:
      - id: bar
"""
        )

        # Act
        with change_cwd(uv_init_repo_dir):
            _pre_commit()

        # Assert
        contents = (uv_init_repo_dir / ".pre-commit-config.yaml").read_text()
        assert contents == (
            """
repos:
  - repo: foo
    hooks:
      - id: bar
"""
        )

    def test_bad_commit(self, uv_init_repo_dir: Path):
        # Act
        with change_cwd(uv_init_repo_dir):
            _pre_commit()
        subprocess.run(["git", "add", "."], cwd=uv_init_repo_dir, check=True)
        subprocess.run(
            ["git", "commit", "-m", "Good commit"], cwd=uv_init_repo_dir, check=True
        )

        # Assert
        with pytest.raises(subprocess.CalledProcessError):
            (uv_init_repo_dir / "pyproject.toml").write_text("[")
            subprocess.run(["git", "add", "."], cwd=uv_init_repo_dir, check=True)
            subprocess.run(
                ["git", "commit", "-m", "Bad commit"], cwd=uv_init_repo_dir, check=True
            )

    def test_cli_pass(self, uv_init_repo_dir: Path):
        subprocess.run(
            ["usethis", "tool", "pre-commit"], cwd=uv_init_repo_dir, check=True
        )

        subprocess.run(
            ["uv", "run", "pre-commit", "run", "--all-files"],
            cwd=uv_init_repo_dir,
            check=True,
        )

    def test_cli_fail(self, uv_init_repo_dir: Path):
        subprocess.run(
            ["usethis", "tool", "pre-commit"], cwd=uv_init_repo_dir, check=True
        )

        # Pass invalid TOML to fail the pre-commit for validate-pyproject
        (uv_init_repo_dir / "pyproject.toml").write_text("[")
        try:
            subprocess.run(
                ["uv", "run", "pre-commit", "run", "--all-files"],
                cwd=uv_init_repo_dir,
                check=True,
            )
        except subprocess.CalledProcessError:
            pass
        else:
            pytest.fail("Expected subprocess.CalledProcessError")


class TestDeptry:
    def test_dependency_added(self, uv_init_dir: Path):
        # Act
        with change_cwd(uv_init_dir):
            _deptry()

        # Assert
        (dev_dep,) = get_dev_deps(uv_init_dir)
        assert dev_dep == "deptry"

    def test_stdout(self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]):
        # Act
        with change_cwd(uv_init_dir):
            _deptry()

        # Assert
        out, _ = capfd.readouterr()
        assert out == (
            "✔ Adding 'deptry' as a development dependency.\n"
            "☐ Call the 'deptry src' command to run deptry.\n"
        )

    def test_run_deptry_fail(self, uv_init_dir: Path):
        # Arrange
        f = uv_init_dir / "bad.py"
        f.write_text("import broken_dependency")

        # Act
        with change_cwd(uv_init_dir):
            _deptry()

        # Assert
        with pytest.raises(subprocess.CalledProcessError):
            subprocess.run(["deptry", "."], cwd=uv_init_dir, check=True)

    def test_run_deptry_pass(self, uv_init_dir: Path):
        # Arrange
        f = uv_init_dir / "good.py"
        f.write_text("import sys")

        # Act
        with change_cwd(uv_init_dir):
            _deptry()

        # Assert
        subprocess.run(["deptry", "."], cwd=uv_init_dir, check=True)

    def test_cli(self, uv_init_dir: Path):
        subprocess.run(["usethis", "tool", "deptry"], cwd=uv_init_dir, check=True)

    def test_pre_commit_after(
        self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]
    ):
        # Act
        with change_cwd(uv_init_dir):
            _deptry()
            _pre_commit()

        # Assert
        # 1. File exists
        assert (uv_init_dir / ".pre-commit-config.yaml").exists()

        # 2. Hook is in the file
        assert "deptry" in get_hook_names(uv_init_dir)

        # 3. Test file contents
        assert (uv_init_dir / ".pre-commit-config.yaml").read_text() == (
            f"""repos:
  - repo: https://github.com/abravalheri/validate-pyproject
    rev: {_VALIDATEPYPROJECT_VERSION}
    hooks:
      - id: validate-pyproject
        additional_dependencies: ['validate-pyproject-schema-store[all]']
  - repo: local
    hooks:
      - id: deptry
        name: deptry
        entry: uv run --frozen deptry src
        language: system
        always_run: true
        pass_filenames: false
"""
        )

        # 4. Check messages
        out, _ = capfd.readouterr()
        assert out == (
            "✔ Adding 'deptry' as a development dependency.\n"
            "☐ Call the 'deptry src' command to run deptry.\n"
            "✔ Adding 'pre-commit' as a development dependency.\n"
            "✔ Writing '.pre-commit-config.yaml'.\n"
            "✔ Adding deptry config to '.pre-commit-config.yaml'.\n"
            "✔ Ensuring pre-commit hooks are installed.\n"
            "☐ Call the 'pre-commit run --all-files' command to run the hooks manually.\n"
        )

    def test_pre_commit_first(
        self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]
    ):
        # Act
        with change_cwd(uv_init_dir):
            _pre_commit()
            _deptry()

        # Assert
        # 1. File exists
        assert (uv_init_dir / ".pre-commit-config.yaml").exists()

        # 2. Hook is in the file
        assert "deptry" in get_hook_names(uv_init_dir)

        # 3. Test file contents
        assert (uv_init_dir / ".pre-commit-config.yaml").read_text() == (
            f"""repos:
  - repo: https://github.com/abravalheri/validate-pyproject
    rev: {_VALIDATEPYPROJECT_VERSION}
    hooks:
      - id: validate-pyproject
        additional_dependencies: ['validate-pyproject-schema-store[all]']
  - repo: local
    hooks:
      - id: deptry
        name: deptry
        entry: uv run --frozen deptry src
        language: system
        always_run: true
        pass_filenames: false
"""
        )

        # 4. Check messages
        out, _ = capfd.readouterr()
        assert out == (
            "✔ Adding 'pre-commit' as a development dependency.\n"
            "✔ Writing '.pre-commit-config.yaml'.\n"
            "✔ Ensuring pre-commit hooks are installed.\n"
            "☐ Call the 'pre-commit run --all-files' command to run the hooks manually.\n"
            "✔ Adding 'deptry' as a development dependency.\n"
            "✔ Adding deptry config to '.pre-commit-config.yaml'.\n"
            "☐ Call the 'deptry src' command to run deptry.\n"
        )


class TestRuff:
    def test_dependency_added(self, uv_init_dir: Path):
        # Act
        with change_cwd(uv_init_dir):
            _ruff()

        # Assert
        (dev_dep,) = get_dev_deps(uv_init_dir)
        assert dev_dep == "ruff"

    def test_stdout(self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]):
        # Act
        with change_cwd(uv_init_dir):
            _ruff()

        # Assert
        out, _ = capfd.readouterr()
        assert out == (
            "✔ Adding 'ruff' as a development dependency.\n"
            "✔ Adding ruff config to 'pyproject.toml'.\n"
            "✔ Enabling ruff rules 'C4', 'E4', 'E7', 'E9', 'F', 'FURB', 'I', 'PLE', 'PLR', \n'PT', 'RUF', 'SIM', 'UP' in 'pyproject.toml'.\n"
            "☐ Call the 'ruff check' command to run the ruff linter.\n"
            "☐ Call the 'ruff format' command to run the ruff formatter.\n"
        )

    def test_cli(self, uv_init_dir: Path):
        subprocess.run(["usethis", "tool", "ruff"], cwd=uv_init_dir, check=True)

    def test_pre_commit_first(
        self, uv_init_dir: Path, capfd: pytest.CaptureFixture[str]
    ):
        # Act
        with change_cwd(uv_init_dir):
            _ruff()
            _pre_commit()

        # Assert
        assert "ruff-format" in get_hook_names(uv_init_dir)
        assert "ruff-check" in get_hook_names(uv_init_dir)


class TestAllHooksList:
    def test_subset_hook_names(self):
        for tool in ALL_TOOLS:
            try:
                hook_names = [
                    hook.id for hook in tool.get_pre_commit_repo_config().hooks
                ]
            except NotImplementedError:
                continue
            for hook_name in hook_names:
                assert hook_name in _HOOK_ORDER
