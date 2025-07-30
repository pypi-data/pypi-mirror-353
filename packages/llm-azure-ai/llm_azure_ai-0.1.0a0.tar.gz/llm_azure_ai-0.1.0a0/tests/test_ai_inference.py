import json

import llm
import pydantic
import pytest


@pytest.mark.vcr
def test_prompt():
    model = llm.get_model("azure/ai-inference-model")

    response = model.prompt("Say hello. All lowercase, no punctuation.", stream=False)
    assert str(response) == "hello"


@pytest.mark.vcr
def test_streaming_prompt():
    model = llm.get_model("azure/ai-inference-model")

    response = model.prompt("Say hello. All lowercase, no punctuation.", stream=True)
    assert str(response) == "hello"


@pytest.mark.vcr
def test_schema():
    class Dog(pydantic.BaseModel):
        name: str
        age: int

    model = llm.get_model("azure/ai-inference-model")
    response = model.prompt("Describe a nice dog", schema=Dog)
    assert json.loads(response.text()) == {"age": 4, "name": "Buddy"}
