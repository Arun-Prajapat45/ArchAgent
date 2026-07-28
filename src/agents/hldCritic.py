from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from pydantic import SecretStr

from ..utils.models import CriticReview
from ..utils.prompts import CriticPromptTemplate


class SystemDesignCriticRAG:
    """Review HLDs against retrieved architecture guidance."""

    def __init__(self, raw_data_dir: Path, vectorstore_path: str, top_k: int = 4) -> None:
        del vectorstore_path
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            raise RuntimeError("OPENROUTER_API_KEY is required")
        embeddings = OpenAIEmbeddings(
            model=os.getenv("OPENROUTER_EMBEDDING_MODEL", "openai/text-embedding-3-small"),
            api_key=SecretStr(api_key),
            base_url="https://openrouter.ai/api/v1",
            timeout=15,
            max_retries=2,
        )
        documents = TextLoader(str(raw_data_dir / "combined.txt"), encoding="utf-8").load()
        chunks = CharacterTextSplitter(chunk_size=800, chunk_overlap=100).split_documents(documents)
        self.retriever = FAISS.from_documents(chunks, embeddings).as_retriever(
            search_kwargs={"k": top_k}
        )
        llm = ChatOpenAI(
            model=os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct:free"),
            api_key=SecretStr(api_key),
            base_url="https://openrouter.ai/api/v1",
            temperature=0.1,
            timeout=45,
            max_retries=2,
        )
        self.structured_llm = llm.with_structured_output(CriticReview)

    def review_design(self, design: Any) -> CriticReview:
        data = design.model_dump() if hasattr(design, "model_dump") else design
        serialized = json.dumps(data)
        context = "\n\n".join(
            document.page_content for document in self.retriever.invoke(serialized)
        )
        prompt = CriticPromptTemplate.format(hld_json=serialized)
        result = self.structured_llm.invoke(f"{prompt}\n\nRetrieved context:\n{context}")
        return CriticReview.model_validate(result)
