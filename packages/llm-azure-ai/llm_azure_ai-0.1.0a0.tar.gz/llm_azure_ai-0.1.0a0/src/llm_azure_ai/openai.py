import json
import typing

import llm
import openai

from openai.types import chat


class AzureOpenAIChat(llm.Model):
    can_stream = True
    supports_schema = True
    supports_tools = True

    def __init__(
        self,
        model_id: str,
        api_version: str,
        endpoint: str,
        credential: str,
        model_name: str,
    ):
        self.model_id = model_id
        self.api_version = api_version
        self.endpoint = endpoint
        self.credential = credential
        self.model_name = model_name

    def __str__(self) -> str:
        return f"Azure OpenAI: {self.model_id}"

    def execute(
        self,
        prompt: llm.Prompt,
        stream: bool,
        response: llm.Response,
        conversation: llm.Conversation,
    ) -> typing.Iterator[str]:
        client = openai.AzureOpenAI(
            api_version=self.api_version,
            azure_endpoint=self.endpoint,
            api_key=self.credential,
        )

        completion = client.chat.completions.create(
            model=self.model_name,
            messages=build_messages(prompt, conversation),
            stream=stream,
            **build_kwargs(prompt),
        )

        if stream:
            yield from handle_streamed_completion(completion, response)
        else:
            yield from handle_completion(completion, response)


def handle_completion(
    completion: chat.ChatCompletion, response: llm.Response
) -> typing.Iterable[str]:
    message = completion.choices[0].message

    if message.tool_calls:
        for tool_call in message.tool_calls:
            local_tool_call = llm.ToolCall(
                tool_call_id=tool_call.id,
                name=tool_call.function.name,
                arguments=json.loads(tool_call.function.arguments),
            )
            response.add_tool_call(local_tool_call)

    if message.content:
        yield message.content


def handle_streamed_completion(
    completion_chunks: openai.Stream[chat.ChatCompletionChunk], response: llm.Response
) -> typing.Iterable[str]:
    for chunk in completion_chunks:
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta

        if delta.tool_calls:
            for tool_call in delta.tool_calls:
                # No idea why we receive these empty tool calls from Azure OpenAI
                if not tool_call.id or not tool_call.function.name:
                    continue

                local_tool_call = llm.ToolCall(
                    tool_call_id=tool_call.id,
                    name=tool_call.function.name,
                    arguments=json.loads(tool_call.function.arguments)
                    if tool_call.function.arguments
                    else {},
                )
                response.add_tool_call(local_tool_call)

        if delta.content:
            yield chunk.choices[0].delta.content


def build_messages_from_prompt(
    prompt: llm.Prompt,
) -> typing.Iterable[chat.ChatCompletionMessageParam]:
    if prompt.system:
        yield chat.ChatCompletionSystemMessageParam(
            role="system", content=prompt.system
        )

    for tool_result in prompt.tool_results:
        yield chat.ChatCompletionToolMessageParam(
            role="tool",
            tool_call_id=tool_result.tool_call_id,
            content=tool_result.output,
        )

    if prompt.prompt:
        yield chat.ChatCompletionUserMessageParam(role="user", content=prompt.prompt)


def build_messages(
    prompt: llm.Prompt, conversation: typing.Optional[llm.Conversation]
) -> typing.Iterable[chat.ChatCompletionMessageParam]:
    messages = []

    if conversation:
        messages += build_messages_from_conversation(conversation)

    messages += build_messages_from_prompt(prompt)

    return remove_repeating_system_prompts(messages)


def build_messages_from_conversation(
    conversation: llm.Conversation,
) -> typing.Iterable[chat.ChatCompletionMessageParam]:
    for response in conversation.responses:  # type: llm.Response
        yield from build_messages_from_prompt(response.prompt)

        assistant_response = response.text_or_raise()
        if assistant_response:
            yield chat.ChatCompletionAssistantMessageParam(
                role="assistant", content=assistant_response
            )

        tool_calls = response.tool_calls_or_raise()
        if tool_calls:
            chat_tool_calls = [
                chat.ChatCompletionMessageToolCallParam(
                    type="function",
                    id=tool_call.tool_call_id,
                    function={
                        "name": tool_call.name,
                        "arguments": json.dumps(tool_call.arguments),
                    },
                )
                for tool_call in tool_calls
            ]
            yield chat.ChatCompletionAssistantMessageParam(
                role="assistant", tool_calls=chat_tool_calls
            )


def remove_repeating_system_prompts(
    messages: typing.Iterable[chat.ChatCompletionMessageParam],
) -> typing.Iterable[chat.ChatCompletionMessageParam]:
    latest_system_prompt = None

    for message in messages:
        if message["role"] != "system":
            yield message
            continue

        if message["content"] != latest_system_prompt:
            latest_system_prompt = message["content"]
            yield message


def build_kwargs(prompt: llm.Prompt) -> dict[str, typing.Any]:
    kwargs = {}

    if prompt.schema:
        kwargs["response_format"] = {
            "type": "json_schema",
            "json_schema": {"name": "output", "schema": prompt.schema},
        }

    if prompt.tools:
        kwargs["tools"] = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or None,
                    "parameters": tool.input_schema,
                },
            }
            for tool in prompt.tools
        ]

    return kwargs


class AzureOpenAIEmbedding(llm.EmbeddingModel):
    def __init__(
        self,
        model_id: str,
        api_version: str,
        endpoint: str,
        credential: str,
        model_name: str,
    ):
        self.model_id = model_id
        self.api_version = api_version
        self.endpoint = endpoint
        self.credential = credential
        self.model_name = model_name

    def __str__(self) -> str:
        return f"Azure OpenAI: {self.model_id}"

    def embed_batch(
        self, items: typing.Iterable[typing.Union[str, bytes]]
    ) -> typing.Iterable[list[float]]:
        client = openai.AzureOpenAI(
            api_version=self.api_version,
            azure_endpoint=self.endpoint,
            api_key=self.credential,
        )

        response = client.embeddings.create(model=self.model_name, input=items)

        for item in response.data:
            yield item.embedding
