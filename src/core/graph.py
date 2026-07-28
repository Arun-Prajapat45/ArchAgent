from __future__ import annotations

from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from src.core.subgraphs.diagram import diagramBuilder
from src.core.subgraphs.hld import hldBuilder
from src.core.subgraphs.requirements import requirementBuilder
from src.utils.models import RequirementModel, SystemDesignSchema


class MainState(TypedDict, total=False):
    user_input: str
    system_requirements: RequirementModel
    system_design: SystemDesignSchema
    output_code: str


def gather_requirements(state: MainState) -> dict[str, Any]:
    final_state = requirementBuilder().invoke({"user_input": state["user_input"]})
    return {"system_requirements": final_state["output_model"]}


def create_design(state: MainState) -> dict[str, Any]:
    final_state = hldBuilder().invoke({"goal": state["system_requirements"]})
    return {"system_design": final_state["generator_output"]}


def create_diagram(state: MainState) -> dict[str, Any]:
    final_state = diagramBuilder().invoke({"input_design": state["system_design"]})
    return {"output_code": final_state["output_code"]}


def builder() -> Any:
    workflow = StateGraph(MainState)
    workflow.add_node("gather_requirements", gather_requirements)
    workflow.add_node("create_design", create_design)
    workflow.add_node("create_diagram", create_diagram)
    workflow.add_edge(START, "gather_requirements")
    workflow.add_edge("gather_requirements", "create_design")
    workflow.add_edge("create_design", "create_diagram")
    workflow.add_edge("create_diagram", END)
    return workflow.compile()
