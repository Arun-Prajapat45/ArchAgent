from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


class RequirementsAgent(Protocol):
    def run(self, prompt: str) -> dict[str, Any]: ...


class DesignAgent(Protocol):
    def run(
        self, requirements: dict[str, Any], feedback: dict[str, Any] | None
    ) -> dict[str, Any]: ...


class CriticAgent(Protocol):
    def run(self, design: dict[str, Any]) -> dict[str, Any]: ...


class DiagramAgent(Protocol):
    def run(self, design: dict[str, Any]) -> str: ...


@dataclass(frozen=True)
class CritiqueResult:
    design: dict[str, Any]
    final_review: dict[str, Any]
    iterations: int


class CritiqueLoop:
    def __init__(self, designer: DesignAgent, critic: CriticAgent, max_iterations: int = 3) -> None:
        if max_iterations < 1:
            raise ValueError("max_iterations must be at least one")
        self.designer = designer
        self.critic = critic
        self.max_iterations = max_iterations

    def run(self, requirements: dict[str, Any]) -> CritiqueResult:
        design: dict[str, Any] = {}
        review: dict[str, Any] | None = None
        for _ in range(self.max_iterations):
            design = self.designer.run(requirements, review)
            review = self.critic.run(design)
        return CritiqueResult(
            design=design, final_review=review or {}, iterations=self.max_iterations
        )


@dataclass(frozen=True)
class PipelineResult:
    requirements: dict[str, Any]
    design: dict[str, Any]
    mermaid: str
    critique_iterations: int


class Pipeline:
    def __init__(
        self, requirements: RequirementsAgent, design_loop: CritiqueLoop, diagram: DiagramAgent
    ) -> None:
        self.requirements = requirements
        self.design_loop = design_loop
        self.diagram = diagram

    def run(self, prompt: str) -> PipelineResult:
        requirements = self.requirements.run(prompt)
        critique = self.design_loop.run(requirements)
        mermaid = self.diagram.run(critique.design)
        return PipelineResult(requirements, critique.design, mermaid, critique.iterations)
