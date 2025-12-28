import logging
import time
import uuid

from llm.generate_answer import generate_answer

logger = logging.getLogger(__name__)


class LLMService:
    def answer(self, question: str, evidence_context: str) -> str:
        request_id = str(uuid.uuid4())
        start_time = time.perf_counter()

        logger.info(
            "LLM generation started",
            extra={
                "request_id": request_id,
                "component": "llm",
            },
        )

        try:
            result = generate_answer(
                question=question,
                evidence_context=evidence_context,
            )

            latency_ms = (time.perf_counter() - start_time) * 1000

            logger.info(
                "LLM generation completed",
                extra={
                    "request_id": request_id,
                    "component": "llm",
                    "latency_ms": round(latency_ms, 2),
                },
            )

            return result["answer"]

        except Exception:
            latency_ms = (time.perf_counter() - start_time) * 1000

            logger.exception(
                "LLM generation failed",
                extra={
                    "request_id": request_id,
                    "component": "llm",
                    "latency_ms": round(latency_ms, 2),
                },
            )
            raise