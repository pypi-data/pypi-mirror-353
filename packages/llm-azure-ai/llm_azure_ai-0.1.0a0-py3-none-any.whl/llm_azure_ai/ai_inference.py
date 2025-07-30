import typing

import llm
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage, JsonSchemaFormat
from azure.core.credentials import AzureKeyCredential


class AzureAIInferenceChat(llm.Model):
    can_stream = True
    supports_schema = True

    def __init__(self, model_id: str, endpoint: str, credential: str, model_name: str):
        self.model_id = model_id
        self.endpoint = endpoint
        self.credential = credential
        self.model_name = model_name

    def __str__(self):
        return f"Azure AI Inference: {self.model_id}"

    def execute(
        self,
        prompt: llm.Prompt,
        stream: bool,
        response: llm.Response,
        conversation: llm.Conversation,
    ) -> typing.Iterator[str]:
        client = ChatCompletionsClient(
            endpoint=self.endpoint,
            credential=AzureKeyCredential(self.credential),
            api_version="2024-08-01-preview",  # required to support JSON schema
        )

        response = client.complete(
            model=self.model_name,
            messages=build_messages(prompt),
            stream=stream,
            **build_kwargs(prompt),
        )

        if stream:
            for update in response:
                if update.choices and update.choices[0].delta.content:
                    yield update.choices[0].delta.content
        else:
            yield response.choices[0].message.content


def build_messages(prompt: llm.Prompt) -> typing.Iterable[str]:
    messages = []

    if prompt.system:
        messages.append(SystemMessage(content=prompt.system))

    messages.append(UserMessage(content=prompt.prompt))

    return messages


def build_kwargs(prompt: llm.Prompt) -> dict[str, typing.Any]:
    kwargs = {}

    if prompt.schema:
        kwargs["response_format"] = JsonSchemaFormat(
            name="output", schema=prompt.schema
        )

    return kwargs
