.PHONY: test record fix

test:
	LLM_AZURE_AI_CONFIG_PATH=$(PWD)/tests/test_config_file.yaml uv run pytest

record:
	LLM_AZURE_AI_CONFIG_PATH=$(PWD)/tests/test_config_file.yaml uv run pytest --record-mode once

fix:
	uv run ruff check --fix src
	uv run ruff format src tests
