from __future__ import annotations

import re


class MermaidValidationError(ValueError):
    pass


_ALLOWED_START = re.compile(r"^(flowchart|graph|sequenceDiagram|classDiagram|stateDiagram-v2|erDiagram)\b")


def normalize_mermaid(text: str) -> str:
    code = text.strip()
    if code.startswith("```mermaid"):
        code = code[len("```mermaid") :]
    elif code.startswith("```"):
        code = code[3:]
    if code.endswith("```"):
        code = code[:-3]
    code = code.strip()
    validate_mermaid(code)
    return code


def validate_mermaid(code: str) -> None:
    """Perform deterministic safety/shape checks before returning Mermaid code.

    Full grammar validation is performed in CI with Mermaid CLI for published examples.
    """
    if not _ALLOWED_START.match(code):
        raise MermaidValidationError("unsupported or missing Mermaid diagram declaration")
    if "%%{" in code or "<script" in code.lower() or "javascript:" in code.lower():
        raise MermaidValidationError("unsafe Mermaid directive")
    for opening, closing in (("[", "]"), ("(", ")"), ("{", "}")):
        if code.count(opening) != code.count(closing):
            raise MermaidValidationError(f"unbalanced {opening}{closing} delimiters")
