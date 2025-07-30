import enum

import llm
import pydantic
import os
import pathlib
import yaml
import sys

from .ai_inference import AzureAIInferenceChat
from .openai import AzureOpenAIChat, AzureOpenAIEmbedding


class SDK(enum.Enum):
    AI_INFERENCE = "ai_inference"
    OPENAI = "openai"


class ModelConfig(pydantic.BaseModel):
    model_id: str
    sdk: SDK
    aliases: list[str] = []
    sdk_config: dict


class Config(pydantic.BaseModel):
    chat_models: list[ModelConfig] = []
    embedding_models: list[ModelConfig] = []


class AzureAIInferenceSDKConfig(pydantic.BaseModel):
    endpoint: pydantic.HttpUrl
    credential: str
    model_name: str


class AzureOpenAISDKConfig(pydantic.BaseModel):
    api_version: str
    endpoint: pydantic.HttpUrl
    credential: str
    model_name: str


def get_config_path() -> pathlib.Path:
    config_path = pathlib.Path(
        os.environ.get("LLM_AZURE_AI_CONFIG_PATH", "llm-azure-ai.yaml")
    )

    if not config_path.is_absolute():
        config_path = llm.user_dir() / config_path

    return config_path


def ensure_config_file_exists(config_path: pathlib.Path):
    if config_path.exists():
        return

    default_config = Config(
        chat_models=[
            ModelConfig(
                model_id="azure/your-ai-inference-model",
                sdk=SDK.AI_INFERENCE,
                sdk_config=AzureAIInferenceSDKConfig(
                    endpoint=pydantic.HttpUrl("https://endpoint.models.ai.azure.com/"),
                    credential="%your-credential%",
                    model_name="%your-model-name%",
                ).model_dump(mode="json"),
            ).model_dump(mode="json"),
            ModelConfig(
                model_id="azure/your-openai-model",
                sdk=SDK.OPENAI,
                sdk_config=AzureOpenAISDKConfig(
                    api_version="%your-api-version%",
                    endpoint=pydantic.HttpUrl("https://endpoint.openai.azure.com/"),
                    credential="%your-credential%",
                    model_name="%your-model-name%",
                ).model_dump(mode="json"),
            ).model_dump(mode="json"),
        ],
        embedding_models=[
            ModelConfig(
                model_id="azure/your-openai-embedding-model",
                sdk=SDK.OPENAI,
                sdk_config=AzureOpenAISDKConfig(
                    api_version="%your-api-version%",
                    endpoint=pydantic.HttpUrl("https://endpoint.openai.azure.com/"),
                    credential="%your-credential%",
                    model_name="%your-model-name%",
                ).model_dump(mode="json"),
            ).model_dump(mode="json"),
        ],
    ).model_dump(mode="json")

    with open(config_path, "w") as f:
        yaml.dump(default_config, f)

    print(
        (
            "No configuration file found for llm-azure-ai. A default one has been created at:\n\n"
            f"{config_path}\n\n"
            "Before you can use this plugin, you need to edit this file and provide your Azure credentials and model configuration."
        )
    )

    sys.exit(1)


@llm.hookimpl
def register_models(register):
    config_path = get_config_path()
    ensure_config_file_exists(config_path)

    with open(config_path) as f:
        config = Config(**yaml.safe_load(f))

    for model_config in config.chat_models:
        if model_config.sdk == SDK.AI_INFERENCE:
            sdk_config = AzureAIInferenceSDKConfig(**model_config.sdk_config)
            register(
                AzureAIInferenceChat(
                    model_id=model_config.model_id,
                    endpoint=sdk_config.endpoint.unicode_string(),
                    credential=sdk_config.credential,
                    model_name=sdk_config.model_name,
                ),
                aliases=model_config.aliases,
            )
        else:
            sdk_config = AzureOpenAISDKConfig(**model_config.sdk_config)
            register(
                AzureOpenAIChat(
                    model_id=model_config.model_id,
                    api_version=sdk_config.api_version,
                    endpoint=sdk_config.endpoint.unicode_string(),
                    credential=sdk_config.credential,
                    model_name=sdk_config.model_name,
                ),
                aliases=model_config.aliases,
            )


@llm.hookimpl
def register_embedding_models(register):
    config_path = get_config_path()
    ensure_config_file_exists(config_path)

    with open(config_path) as f:
        config = Config(**yaml.safe_load(f))

    for model_config in config.embedding_models:
        sdk_config = AzureOpenAISDKConfig(**model_config.sdk_config)
        model = AzureOpenAIEmbedding(
            model_id=model_config.model_id,
            api_version=sdk_config.api_version,
            endpoint=sdk_config.endpoint.unicode_string(),
            credential=sdk_config.credential,
            model_name=sdk_config.model_name,
        )
        register(model, aliases=model_config.aliases)
