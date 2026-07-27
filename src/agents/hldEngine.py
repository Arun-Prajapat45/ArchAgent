from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter

from ..utils.models import SystemDesignSchema
from ..utils.prompts import DesignGeneratorTemplate, DesignUpdateTemplate


class SystemDesignRAG:
    """Generate and refine a validated HLD using retrieved architecture context."""

    def __init__(
        self,
        raw_data_dir: Path,
        vectorstore_path: str,
        chunk_size: int = 800,
        chunk_overlap: int = 100,
        top_k: int = 4,
    ) -> None:
        del vectorstore_path
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            raise RuntimeError("OPENROUTER_API_KEY is required")
        embeddings = OpenAIEmbeddings(
            model=os.getenv("OPENROUTER_EMBEDDING_MODEL", "openai/text-embedding-3-small"),
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            request_timeout=15,
            max_retries=2,
        )
        documents = TextLoader(str(raw_data_dir / "combined.txt"), encoding="utf-8").load()
        chunks = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap).split_documents(documents)
        self.retriever = FAISS.from_documents(chunks, embeddings).as_retriever(search_kwargs={"k": top_k})
        llm = ChatOpenAI(
            model=os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct:free"),
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            temperature=0.15,
            request_timeout=45,
            max_retries=2,
        )
        self.structured_llm = llm.with_structured_output(SystemDesignSchema)

    def _context(self, query: str) -> str:
        return "\n\n".join(document.page_content for document in self.retriever.invoke(query))

    def generate_design(self, goal: Any) -> SystemDesignSchema:
        data = goal.model_dump() if hasattr(goal, "model_dump") else dict(goal)
        metrics = data["strategic_8_metrics"]
        prompt = DesignGeneratorTemplate.format(
            archetype=data["identification"]["archetype"],
            core_action=metrics["core_action"],
            input=metrics["io_contract"]["input"],
            output=metrics["io_contract"]["output"],
            read_write_ratio=metrics["read_write_ratio"],
            consistency_model=metrics["consistency_model"],
            functional=data["requirements_summary"]["functional"],
            non_functional=data["requirements_summary"]["non_functional"],
        )
        return self.structured_llm.invoke(
            f"{prompt}\n\nRetrieved context:\n{self._context(prompt)}"
        )

    def update_design(self, goal: Any, current: Any, feedback: Any) -> SystemDesignSchema:
        goal_data = goal.model_dump() if hasattr(goal, "model_dump") else goal
        current_data = current.model_dump() if hasattr(current, "model_dump") else current
        feedback_data = feedback.model_dump() if hasattr(feedback, "model_dump") else feedback
        prompt = DesignUpdateTemplate.format(
            user_input=json.dumps(goal_data),
            hld_output_json=json.dumps(current_data),
            critic_feedback_json=json.dumps(feedback_data),
        )
        return self.structured_llm.invoke(
            f"{prompt}\n\nRetrieved context:\n{self._context(prompt)}"
        )
