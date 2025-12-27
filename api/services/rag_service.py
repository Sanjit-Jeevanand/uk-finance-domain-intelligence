from typing import Dict, List
from retrieval.embed_query import QueryEmbedder
from retrieval.similarity_search import load_faiss, search
from retrieval.filters import apply_filters
from retrieval.build_evidence import build_evidence_context


class RAGService:
    def __init__(self):
        self.embedder = QueryEmbedder("all-MiniLM-L6-v2")
        self.index, self.metadata = load_faiss()

    def retrieve(
        self,
        query: str,
        filters: Dict,
        top_k: int = 5,
    ) -> Dict:
        # Embed query
        query_embedding = self.embedder.embed(query)

        # Similarity search
        results = search(
            self.index,
            self.metadata,
            query_embedding,
            top_k=top_k * 2,  # overfetch, filter later
        )

        # Metadata filters
        filtered = apply_filters(results, filters)

        # Evidence context
        evidence_context = build_evidence_context(
            filtered[:top_k]
        )

        return {
            "raw_chunks": filtered[:top_k],
            "evidence_context": evidence_context,
        }