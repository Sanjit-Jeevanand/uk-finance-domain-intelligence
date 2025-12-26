from retrieval.embed_query import QueryEmbedder
from retrieval.similarity_search import load_faiss, search
from retrieval.filters import apply_filters
from retrieval.build_evidence import build_evidence_context

embedder = QueryEmbedder("all-MiniLM-L6-v2")
query = "What risks did Barclays highlight in 2024?"

q_emb = embedder.embed(query)

index, metadata = load_faiss()
results = search(index, metadata, q_emb, top_k=10)

filtered = apply_filters(
    results,
    filters={
        "company": "Barclays",
        "fiscal_year": 2024,
        "report_type": "annual_report"
    }
)

evidence = build_evidence_context(filtered[:5])
print(evidence)
print("Evidence length:", len(evidence))