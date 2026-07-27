from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import MarkdownHeaderTextSplitter


class RequirementsRAG:
    """Retrieve architecture archetypes and return validated requirements."""

    def __init__(
        self,
        raw_data_dir: Path,
        vectorstore_path: str,
        requirement_model: type[Any],
        requirements_prompt: str,
        file_name: str = "requirements2.txt",
        k: int = 5,
    ) -> None:
        del vectorstore_path  # Unsafe pickle-backed indexes are intentionally not loaded.
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            raise RuntimeError("OPENROUTER_API_KEY is required")
        self.requirement_model = requirement_model
        self.requirements_prompt = requirements_prompt
        self.k = k
        embeddings = OpenAIEmbeddings(
            model=os.getenv("OPENROUTER_EMBEDDING_MODEL", "openai/text-embedding-3-small"),
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            request_timeout=15,
            max_retries=2,
        )
        llm = ChatOpenAI(
            model=os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct:free"),
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            temperature=0.15,
            request_timeout=30,
            max_retries=2,
        )
        raw_text = (raw_data_dir / file_name).read_text(encoding="utf-8")
        parents = MarkdownHeaderTextSplitter(headers_to_split_on=[("#", "archetype")]).split_text(raw_text)
        documents = parents or [Document(page_content=raw_text)]
        self.retriever = FAISS.from_documents(documents, embeddings).as_retriever(search_kwargs={"k": k})
        self.structured_llm = llm.with_structured_output(requirement_model)

    def generate_requirements(self, user_input: str) -> Any:
        documents = self.retriever.invoke(user_input)
        context = "\n\n".join(document.page_content for document in documents)
        prompt = self.requirements_prompt.format(query=user_input)
        return self.structured_llm.invoke(
            f"{prompt}\n\nRetrieved architecture context:\n{context}"
        )
