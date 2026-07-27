from __future__ import annotations

import re
from collections import Counter


class InMemoryRetriever:
    """Small deterministic retriever used by tests and evaluation baselines."""

    def __init__(self, documents: list[str]) -> None:
        self.documents = documents

    @staticmethod
    def _tokens(text: str) -> Counter[str]:
        return Counter(re.findall(r"[a-z0-9]+", text.lower()))

    def search(self, query: str, k: int = 3) -> list[str]:
        query_tokens = self._tokens(query)
        ranked = []
        for index, document in enumerate(self.documents):
            overlap = sum((query_tokens & self._tokens(document)).values())
            if overlap:
                ranked.append((overlap, -index, document))
        ranked.sort(reverse=True)
        return [document for _, _, document in ranked[:k]]
