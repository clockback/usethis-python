from pathlib import Path

from typer.testing import CliRunner

from usethis._interface.badge import app
from usethis._test import change_cwd


class TestPyPI:
    def test_add(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke(app, ["pypi"])

        # Assert
        assert result.exit_code == 0, result.output

    def test_remove(self, tmp_path: Path):
        # Arrange
        (tmp_path / "README.md").write_text("")

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke(app, ["pypi", "--remove"])

        # Assert
        assert result.exit_code == 0, result.output


class TestRuff:
    def test_add(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke(app, ["ruff"])

        # Assert
        assert result.exit_code == 0, result.output

    def test_remove(self, tmp_path: Path):
        # Arrange
        (tmp_path / "README.md").write_text("")

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke(app, ["ruff", "--remove"])

        # Assert
        assert result.exit_code == 0, result.output


class TestPreCommit:
    def test_add(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke(app, ["pre-commit"])

        # Assert
        assert result.exit_code == 0, result.output

    def test_remove(self, tmp_path: Path):
        # Arrange
        (tmp_path / "README.md").write_text("")

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke(app, ["pre-commit", "--remove"])

        # Assert
        assert result.exit_code == 0, result.output


class TestUseThis:
    def test_add(self, tmp_path: Path):
        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke(app, ["usethis"])

        # Assert
        assert result.exit_code == 0, result.output

    def test_remove(self, tmp_path: Path):
        # Arrange
        (tmp_path / "README.md").write_text("")

        # Act
        runner = CliRunner()
        with change_cwd(tmp_path):
            result = runner.invoke(app, ["usethis", "--remove"])

        # Assert
        assert result.exit_code == 0, result.output
