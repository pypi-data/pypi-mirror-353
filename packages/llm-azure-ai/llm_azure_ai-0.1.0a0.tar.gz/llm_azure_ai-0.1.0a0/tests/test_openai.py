import json

import llm
import pydantic
import pytest
from openai import models


@pytest.mark.vcr
def test_prompt():
    model = llm.get_model("azure/openai-model")

    response = model.prompt("Say hello. All lowercase, no punctuation.", stream=False)
    assert str(response) == "hello"


@pytest.mark.vcr
def test_streaming_prompt():
    model = llm.get_model("azure/openai-model")

    response = model.prompt("Say hello. All lowercase, no punctuation.", stream=True)
    assert str(response) == "hello"


@pytest.mark.vcr
def test_schema():
    class Dog(pydantic.BaseModel):
        name: str
        age: int

    model = llm.get_model("azure/openai-model")
    response = model.prompt("Describe a nice dog", schema=Dog)
    assert json.loads(response.text()) == {"age": 3, "name": "Buddy"}


@pytest.mark.vcr
def test_conversation():
    system_prompt = "Answer in one word, all lowercase, no punctuation."

    model = llm.get_model("azure/openai-model")
    conversation = model.conversation()

    response = conversation.prompt(
        "My favorite color is blue. What is my favorite color?", system=system_prompt
    )
    assert response.text() == "blue"

    response = conversation.prompt(
        "What is my favorite color again?", system=system_prompt
    )
    assert response.text() == "blue"


@pytest.mark.vcr
def test_tools():
    names = ["Charles", "Sammy"]
    tool = llm.Tool.function(lambda: names.pop(0), name="pelican_name_generator")

    model = llm.get_model("azure/openai-model")
    chain_response = model.chain(
        "Two names for a pet pelican", tools=[tool], stream=False
    )
    text = chain_response.text()

    assert text == "Here are two names for your pet pelican: Charles and Sammy!"


@pytest.mark.vcr
def test_streaming_tools():
    names = ["Charles", "Sammy"]
    tool = llm.Tool.function(lambda: names.pop(0), name="pelican_name_generator")

    model = llm.get_model("azure/openai-model")
    chain_response = model.chain(
        "Two names for a pet pelican", tools=[tool], stream=True
    )
    text = chain_response.text()

    assert text == "Here are two names for a pet pelican: **Charles** and **Sammy**."


@pytest.mark.vcr
def test_embeddings():
    model = llm.get_embedding_model("azure/openai-embedding-model")

    assert model.embed("Hello world")[:5] == [
        -0.002078542485833168,
        -0.04908587411046028,
        0.020946789532899857,
        0.03135102614760399,
        -0.04530530795454979,
    ]
