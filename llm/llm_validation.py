# tests/test_rag_answer.py

from retrieval.embed_query import QueryEmbedder
from retrieval.similarity_search import load_faiss, search
from retrieval.filters import apply_filters
from retrieval.build_evidence import build_evidence_context
from llm.generate_answer import generate_answer


def test_rag_answer():
    question = "What risks did Barclays highlight in 2024?"

    # 1. Embed query
    embedder = QueryEmbedder("all-MiniLM-L6-v2")
    query_embedding = embedder.embed(question)

    # 2. Load FAISS + metadata
    index, metadata = load_faiss()

    # 3. Similarity search
    results = search(index, metadata, query_embedding, top_k=10)

    # 4. Metadata filtering
    filtered = apply_filters(
        results,
        filters={
            "company": "Barclays",
            "fiscal_year": 2024,
            "report_type": "annual_report",
        }
    )

    assert len(filtered) > 0, "No relevant chunks retrieved"

    # 5. Build evidence context
    evidence = build_evidence_context(filtered[:5])

    print("\n=== EVIDENCE CONTEXT ===\n")
    print(evidence[:1000], "...\n")  # sanity check

    # 6. Generate answer
    answer = generate_answer(
        question=question,
        evidence_context=evidence,
    )

    print("\n=== ANSWER ===\n")
    print(answer["answer"])


if __name__ == "__main__":
    test_rag_answer()