from __future__ import annotations

import json
import os
from typing import Any

from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from backend.mermaid import normalize_mermaid

from ..utils.prompts import DiagrammerPromptTemplate


class ArchitectureDiagrammer:
    def __init__(self, prompt: Any = DiagrammerPromptTemplate, llm: Any = None) -> None:
        if llm is None:
            api_key = os.environ.get("OPENROUTER_API_KEY")
            if not api_key:
                raise RuntimeError("OPENROUTER_API_KEY is required")
            llm = ChatOpenAI(
                model=os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct:free"),
                api_key=SecretStr(api_key),
                base_url="https://openrouter.ai/api/v1",
                temperature=0.1,
                timeout=45,
                max_retries=2,
            )
        self.chain = prompt | llm | StrOutputParser()

    def generate_code(self, architecture_json: dict[str, Any]) -> str:
        generated = self.chain.invoke({"arch_json": json.dumps(architecture_json, indent=2)})
        return normalize_mermaid(generated)

    def run(self, architecture_json: dict[str, Any]) -> str:
        return self.generate_code(architecture_json)
