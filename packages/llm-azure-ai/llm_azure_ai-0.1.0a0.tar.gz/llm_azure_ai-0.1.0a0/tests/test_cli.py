from click.testing import CliRunner, Result
from llm.cli import cli


def test_cli(tmpdir, monkeypatch):
    config_path = tmpdir / "config_file.yaml"
    monkeypatch.setenv("LLM_AZURE_AI_CONFIG_PATH", str(config_path))

    # ensure that the config file does not exist before the first run
    assert config_path.exists() == False

    runner = CliRunner()
    result = runner.invoke(cli, ["models"])

    # the exit code should be 1 because the config file was missing
    assert result.exit_code == 1
    # the missing config file message should be visible in the console output
    assert "No configuration file found for llm-azure-ai" in result.output
    # default config file should have been created
    assert config_path.exists()

    result = runner.invoke(cli, ["models"])

    # the file exists now, so the exit code should be 0
    assert result.exit_code == 0

    # the models from the default config file should now be listed
    assert "azure/your-ai-inference-model" in result.output
    assert "azure/your-openai-model" in result.output

    result = runner.invoke(cli, ["embed-models"])

    # the file exists now, so the exit code should be 0
    assert result.exit_code == 0

    # the models from the default config file should now be listed
    assert "azure/your-openai-embedding-model" in result.output
