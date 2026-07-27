from __future__ import annotations

from typing import Any

from backend.mermaid import normalize_mermaid


class LegacyGraphService:
    """Application-scoped adapter around the existing LangGraph workflow."""

    def __init__(self) -> None:
        self._graph: Any = None

    def _get_graph(self) -> Any:
        if self._graph is None:
            from src.core.graph import builder

            self._graph = builder()
        return self._graph

    async def generate(self, prompt: str) -> dict[str, Any]:
        final_state = await self._get_graph().ainvoke({"user_input": prompt})
        requirements = _as_dict(final_state["system_requirements"])
        design = _as_dict(final_state["system_design"])
        return {
            "requirements": requirements,
            "design": design,
            "mermaid": normalize_mermaid(final_state["output_code"]),
            "critique_iterations": 3,
        }


def _as_dict(value: Any) -> dict[str, Any]:
    if hasattr(value, "model_dump"):
        return value.model_dump()
    return dict(value)
