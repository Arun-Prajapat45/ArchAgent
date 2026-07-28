from backend.workflow import CritiqueLoop, Pipeline


class Requirements:
    def run(self, prompt: str) -> dict[str, str]:
        return {"prompt": prompt}


class Designer:
    def __init__(self) -> None:
        self.feedback: list[dict[str, int] | None] = []

    def run(self, requirements: dict[str, str], feedback: dict[str, int] | None) -> dict[str, int]:
        self.feedback.append(feedback)
        return {"revision": len(self.feedback)}


class Critic:
    def __init__(self) -> None:
        self.calls = 0

    def run(self, design: dict[str, int]) -> dict[str, int]:
        self.calls += 1
        return {"reviewed_revision": design["revision"]}


class Diagrammer:
    def run(self, design: dict[str, int]) -> str:
        return f"flowchart LR\nA[Revision {design['revision']}] --> B[Done]"


def test_pipeline_routes_requirements_design_critique_diagram() -> None:
    designer = Designer()
    critic = Critic()
    pipeline = Pipeline(
        Requirements(), CritiqueLoop(designer, critic, max_iterations=3), Diagrammer()
    )

    result = pipeline.run("Build chat")

    assert result.design == {"revision": 3}
    assert critic.calls == 3
    assert designer.feedback == [None, {"reviewed_revision": 1}, {"reviewed_revision": 2}]
    assert result.critique_iterations == 3
    assert result.mermaid.startswith("flowchart")


def test_critique_loop_enforces_configured_maximum() -> None:
    designer, critic = Designer(), Critic()
    result = CritiqueLoop(designer, critic, max_iterations=2).run({"prompt": "x"})
    assert result.iterations == 2
    assert critic.calls == 2
