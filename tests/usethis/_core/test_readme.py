from pathlib import Path

import pytest

from usethis._core.readme import add_readme
from usethis._integrations.pyproject_toml.io_ import pyproject_toml_io_manager
from usethis._test import change_cwd


class TestAddReadme:
    def test_start_from_nothing(
        self, tmp_path: Path, capfd: pytest.CaptureFixture[str]
    ):
        # Act
        with change_cwd(tmp_path), pyproject_toml_io_manager.open():
            add_readme()

        # Assert
        assert (tmp_path / "README.md").exists()
        out, err = capfd.readouterr()
        assert not err
        assert out == (
            "✔ Writing 'pyproject.toml'.\n"
            "✔ Writing 'README.md'.\n"
            "☐ Populate 'README.md' to help users understand the project.\n"
        )

    def test_different_suffix(self, tmp_path: Path):
        # Arrange
        (tmp_path / "README.rst").touch()

        # Act
        with change_cwd(tmp_path), pyproject_toml_io_manager.open():
            add_readme()

        # Assert
        assert not (tmp_path / "README.md").exists()

    def test_readme_directory(self, tmp_path: Path):
        # Arrange
        (tmp_path / "README").mkdir()

        # Act
        with change_cwd(tmp_path), pyproject_toml_io_manager.open():
            add_readme()

        # Assert
        assert (tmp_path / "README.md").exists()

    def test_readme_no_suffix(self, tmp_path: Path, capfd: pytest.CaptureFixture[str]):
        # Arrange
        (tmp_path / "README").touch()

        # Act
        with change_cwd(tmp_path):
            add_readme()

        # Assert
        assert not (tmp_path / "README.md").exists()
        out, err = capfd.readouterr()
        assert not err
        assert not out

    def test_no_pyproject_toml(self, tmp_path: Path):
        # We should automatically generate the TOML file.

        # Act
        with change_cwd(tmp_path), pyproject_toml_io_manager.open():
            add_readme()

        # Assert
        assert (tmp_path / "README.md").exists()
        assert (tmp_path / "README.md").read_text() != ""

    def test_no_project_name_nor_description(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text("")

        # Act
        with change_cwd(tmp_path), pyproject_toml_io_manager.open():
            add_readme()

        # Assert
        assert (tmp_path / "README.md").exists()
        assert (tmp_path / "README.md").read_text() == ""

    def test_no_project_name_only_description(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            """\
[project]
description = "A description"
"""
        )

        # Act
        with change_cwd(tmp_path), pyproject_toml_io_manager.open():
            add_readme()

        # Assert
        assert (tmp_path / "README.md").exists()
        assert (tmp_path / "README.md").read_text() == "A description\n"

    def test_no_project_description_only_name(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            """\
[project]
name = "A name"
"""
        )

        # Act
        with change_cwd(tmp_path), pyproject_toml_io_manager.open():
            add_readme()

        # Assert
        assert (tmp_path / "README.md").exists()
        assert (tmp_path / "README.md").read_text() == "# A name\n"

    def test_project_name_and_description(self, tmp_path: Path):
        # Arrange
        (tmp_path / "pyproject.toml").write_text(
            """\
[project]
name = "A name"
description = "A description"
"""
        )

        # Act
        with change_cwd(tmp_path), pyproject_toml_io_manager.open():
            add_readme()

        # Assert
        assert (tmp_path / "README.md").exists()
        assert (tmp_path / "README.md").read_text() == "# A name\n\nA description\n"
