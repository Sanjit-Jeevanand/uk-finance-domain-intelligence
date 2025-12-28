from typing import Dict, List
from retrieval.embed_query import QueryEmbedder
from retrieval.similarity_search import load_faiss, search
from retrieval.filters import apply_filters
from retrieval.build_evidence import build_evidence_context

import logging
import time
import uuid

logger = logging.getLogger(__name__)


class RAGService:
    def __init__(self):
        self.embedder = QueryEmbedder("all-MiniLM-L6-v2")
        self.index, self.metadata = load_faiss()
        logger.info("rag_service_initialized", extra={"index_loaded": True})

    def retrieve(
        self,
        query: str,
        filters: Dict,
        top_k: int = 5,
    ) -> Dict:
        request_id = str(uuid.uuid4())
        start_time = time.time()

        logger.info(
            "retrieve_started",
            extra={
                "request_id": request_id,
                "top_k": top_k,
                "filters": filters,
            },
        )

        try:
            query_embedding = self.embedder.embed(query)

            results = search(
                self.index,
                self.metadata,
                query_embedding,
                top_k=top_k * 2,
            )

            filtered = apply_filters(results, filters)

            evidence_context = build_evidence_context(
                filtered[:top_k]
            )

            latency_ms = int((time.time() - start_time) * 1000)

            logger.info(
                "retrieve_completed",
                extra={
                    "request_id": request_id,
                    "latency_ms": latency_ms,
                    "returned_chunks": len(filtered[:top_k]),
                },
            )

            return {
                "raw_chunks": filtered[:top_k],
                "evidence_context": evidence_context,
            }

        except Exception:
            logger.exception(
                "retrieve_failed",
                extra={"request_id": request_id},
            )
            raise