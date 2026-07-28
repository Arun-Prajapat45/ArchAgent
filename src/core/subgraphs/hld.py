from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from src.agents.hldCritic import SystemDesignCriticRAG
from src.agents.hldEngine import SystemDesignRAG
from src.utils.models import CriticReview, RequirementModel, SystemDesignSchema

RAW_DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "raw"


class HldState(TypedDict, total=False):
    generator: SystemDesignRAG
    critic: SystemDesignCriticRAG
    goal: RequirementModel
    num_iterations: int
    generator_output: SystemDesignSchema
    critic_output: CriticReview


@lru_cache(maxsize=1)
def _agents() -> tuple[SystemDesignRAG, SystemDesignCriticRAG]:
    return (
        SystemDesignRAG(RAW_DATA_DIR, ""),
        SystemDesignCriticRAG(RAW_DATA_DIR, ""),
    )


def initialize(state: HldState) -> dict[str, Any]:
    del state
    generator, critic = _agents()
    return {"generator": generator, "critic": critic, "num_iterations": 0}


def design(state: HldState) -> dict[str, Any]:
    iteration = state.get("num_iterations", 0) + 1
    if iteration == 1:
        output = state["generator"].generate_design(state["goal"])
    else:
        output = state["generator"].update_design(
            state["goal"], state["generator_output"], state["critic_output"]
        )
    return {"generator_output": output, "num_iterations": iteration}


def evaluate(state: HldState) -> dict[str, Any]:
    return {"critic_output": state["critic"].review_design(state["generator_output"])}


def max_iterations() -> int:
    return min(max(int(os.getenv("CRITIC_MAX_ITERATIONS", "3")), 1), 5)


def should_continue(state: HldState) -> Literal["continue", "end"]:
    return "end" if state["num_iterations"] >= max_iterations() else "continue"


def hldBuilder() -> Any:
    workflow = StateGraph(HldState)
    workflow.add_node("initialize", initialize)
    workflow.add_node("design", design)
    workflow.add_node("evaluate", evaluate)
    workflow.add_edge(START, "initialize")
    workflow.add_edge("initialize", "design")
    workflow.add_edge("design", "evaluate")
    workflow.add_conditional_edges("evaluate", should_continue, {"continue": "design", "end": END})
    return workflow.compile()
