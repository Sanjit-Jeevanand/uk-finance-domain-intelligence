import subprocess
from typing import Dict


SYSTEM_PROMPT = """You are a financial analysis assistant answering questions over official company reports.

Your task:
- Answer the USER QUESTION using ONLY the information in the CONTEXT.
- The CONTEXT consists of extracted excerpts from financial documents.

Strict rules:
- Every factual claim MUST be supported by the provided context.
- Use the provided page numbers for traceability.
- Cite sources at the END of the answer, not inline.
- Each source citation must include:
  - SOURCE number
  - Company name
  - Document type and fiscal year
  - Page range(s) used
- Do NOT use outside knowledge, assumptions, or general financial knowledge.
- Do NOT speculate or infer beyond what is explicitly stated.
- If the context does not fully answer the question, respond exactly with:
  "I do not have enough information in the provided documents."
- Do NOT include reasoning steps, chain-of-thought, or internal analysis.
- Write concise, professional answers suitable for financial and regulatory analysis.

Output format (MANDATORY):

<ANSWER>
A clear, structured answer (tables allowed if appropriate).

---

<SOURCES>
SOURCE [X] — Company, Document, Fiscal Year, Pages A–B
"""


def build_prompt(question: str, context: str) -> str:
    return f"""
SYSTEM:
{SYSTEM_PROMPT}

CONTEXT:
{context}

USER QUESTION:
{question}

ASSISTANT:
""".strip()


def generate_answer(
    question: str,
    evidence_context: str,
    model: str = "gpt-oss:20b",
) -> Dict:
    """
    Generate a grounded answer using a local LLM.

    Returns:
    {
        "answer": str,
        "raw_output": str
    }
    """

    prompt = build_prompt(question, evidence_context)

    process = subprocess.run(
        [
            "ollama",
            "run",
            model,
        ],
        input=prompt,
        text=True,
        capture_output=True,
    )

    if process.returncode != 0:
        raise RuntimeError(process.stderr)

    answer = process.stdout.strip()

    return {
        "answer": answer,
        "raw_output": answer,
    }