from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from src.agents.requirementsClassifier import RequirementsRAG
from src.utils.models import RequirementModel
from src.utils.prompts import RequirementsQuery

RAW_DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "raw"


class RequirementsState(TypedDict, total=False):
    user_input: str
    model: RequirementsRAG
    output_model: RequirementModel


@lru_cache(maxsize=1)
def _model() -> RequirementsRAG:
    return RequirementsRAG(
        raw_data_dir=RAW_DATA_DIR,
        vectorstore_path="",
        requirement_model=RequirementModel,
        requirements_prompt=RequirementsQuery,
    )


def initialize(state: RequirementsState) -> dict[str, Any]:
    del state
    return {"model": _model()}


def generate(state: RequirementsState) -> dict[str, Any]:
    return {"output_model": state["model"].generate_requirements(state["user_input"])}


def requirementBuilder() -> Any:
    workflow = StateGraph(RequirementsState)
    workflow.add_node("initialize", initialize)
    workflow.add_node("generate", generate)
    workflow.add_edge(START, "initialize")
    workflow.add_edge("initialize", "generate")
    workflow.add_edge("generate", END)
    return workflow.compile()
