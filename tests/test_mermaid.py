import pytest

from backend.mermaid import MermaidValidationError, normalize_mermaid, validate_mermaid


def test_normalize_removes_markdown_fence_and_validates() -> None:
    code = normalize_mermaid("```mermaid\nflowchart LR\nA[API] --> B[DB]\n```")
    assert code == "flowchart LR\nA[API] --> B[DB]"
    validate_mermaid(code)


@pytest.mark.parametrize(
    "code", ["hello", "%%{init: {}}%%\nflowchart LR\nA-->B", "flowchart LR\nA[bad"]
)
def test_validator_rejects_unsafe_or_malformed_output(code: str) -> None:
    with pytest.raises(MermaidValidationError):
        validate_mermaid(code)
