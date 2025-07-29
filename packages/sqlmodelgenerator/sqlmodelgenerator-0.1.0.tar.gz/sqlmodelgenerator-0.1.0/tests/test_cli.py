from typer.testing import CliRunner
from sqlmodelgenerator.cli import app

runner = CliRunner()


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "SQLModelGenerator" in result.output
