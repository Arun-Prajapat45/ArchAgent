from __future__ import annotations

from functools import lru_cache
from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from src.agents.diagrammer import ArchitectureDiagrammer
from src.utils.models import SystemDesignSchema


class DiagramState(TypedDict, total=False):
    input_design: SystemDesignSchema | dict[str, Any]
    output_code: str


@lru_cache(maxsize=1)
def _diagrammer() -> ArchitectureDiagrammer:
    return ArchitectureDiagrammer()


def create_diagram(state: DiagramState) -> dict[str, str]:
    design = state["input_design"]
    payload = design.model_dump() if hasattr(design, "model_dump") else design
    return {"output_code": _diagrammer().generate_code(payload)}


def diagramBuilder() -> Any:
    workflow = StateGraph(DiagramState)
    workflow.add_node("create", create_diagram)
    workflow.add_edge(START, "create")
    workflow.add_edge("create", END)
    return workflow.compile()
