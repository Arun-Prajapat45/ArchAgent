from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_source_does_not_enable_unsafe_deserialization() -> None:
    source = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "src").rglob("*.py"))
    assert "allow_dangerous_deserialization=True" not in source
    assert "pickle.load(" not in source


def test_production_graph_compiles_without_external_calls() -> None:
    from src.core.graph import builder

    assert builder() is not None
