from llm.generate_answer import generate_answer


class LLMService:
    def answer(self, question: str, evidence_context: str) -> str:
        result = generate_answer(
            question=question,
            evidence_context=evidence_context,
        )
        return result["answer"]