from backend.retrieval import InMemoryRetriever


def test_retrieval_ranks_relevant_documents_without_network() -> None:
    retriever = InMemoryRetriever(
        ["Kafka event streaming", "PostgreSQL transactions", "Redis caching"]
    )
    assert retriever.search("event Kafka", k=1) == ["Kafka event streaming"]
    assert retriever.search("unmatched", k=2) == []
