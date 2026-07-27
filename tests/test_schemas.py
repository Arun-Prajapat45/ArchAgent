import pytest
from pydantic import ValidationError

from backend.schemas import ChatRequest, Connectivity, RequirementModel


def test_chat_request_rejects_blank_prompt() -> None:
    with pytest.raises(ValidationError):
        ChatRequest(user_input="   ")


def test_requirement_throughput_rejects_negative_values() -> None:
    with pytest.raises(ValidationError):
        RequirementModel.model_validate({
            "archetype": "chat",
            "functional_requirements": ["messaging"],
            "non_functional_requirements": ["low latency"],
            "average_rps": -1,
            "peak_rps": 10,
        })


def test_connectivity_accepts_named_or_three_item_edges() -> None:
    assert Connectivity.model_validate(["Client", "API", "Service"]).intermediary == "API"
    assert Connectivity(source="Client", intermediary="API", destination="Service").destination == "Service"
