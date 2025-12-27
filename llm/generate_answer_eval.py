import subprocess
from typing import Dict
import re
import requests



SYSTEM_PROMPT = """You are a financial analysis assistant answering questions over official company reports.

Your task:
- Answer the USER QUESTION using ONLY the information in the CONTEXT.
- The CONTEXT consists of extracted excerpts from financial documents.

Strict rules:
- Output ONLY the final answer content.
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
- If answering would require inference, summarisation across unrelated excerpts,
  or general financial knowledge, you MUST refuse.
  Refusal is preferred over partial answers.
- If the context does not fully answer the question, respond exactly with:
  "I do not have enough information in the provided documents."
- You MUST preserve modal language exactly as written in the context.
  If the source uses terms such as "could", "may", or "might", you MUST NOT
  restate them as definitive outcomes (e.g. "will", "does", "has").

Exception (controlled):
- You MAY summarise across multiple excerpts IF:
  - All excerpts are from the SAME company
  - All excerpts are from the SAME document
  - All excerpts are from the SAME fiscal year

Output format (MANDATORY):

You MUST wrap your entire answer EXACTLY between the tags <ANSWER> and </ANSWER>.
Do not output anything outside these tags.

<ANSWER>
A clear, structured answer (tables allowed if appropriate).
</ANSWER>

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
    MIN_EVIDENCE_CHARS = 400
    if len(evidence_context.strip()) < MIN_EVIDENCE_CHARS:
        return {
            "answer": "I do not have enough information in the provided documents.",
            "outcome": "REFUSE_OK"
        }

    # --- Company consistency guard ---
    # companies_in_context = set(
    # re.findall(r'"company"\s*:\s*"([^"]+)"', evidence_context, re.IGNORECASE)
    # )   

    # if hasattr(generate_answer, "expected_company"):
    #     if generate_answer.expected_company not in companies_in_context:
    #         return {
    #             "answer": "I do not have enough information in the provided documents."
    #         }

    if not evidence_context.strip():
        return {
            "answer": "I do not have enough information in the provided documents.",
            "outcome": "REFUSE_OK"
        }

    prompt = build_prompt(question, evidence_context)

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0,
                "top_p": 1,
                "repeat_penalty": 1
            }
        },
        timeout=120
    )

    if response.status_code != 200:
        raise RuntimeError(response.text)

    raw_output = response.json().get("response", "")

    # Truncate output before the first <ANSWER> tag
    start_index = raw_output.find("<ANSWER>")
    truncated_output = raw_output[start_index:] if start_index != -1 else raw_output

    match = re.search(
        r"<ANSWER>\s*(.*?)\s*</ANSWER>",
        truncated_output,
        re.DOTALL
    )

    if not match:
        return {
            "answer": "I do not have enough information in the provided documents.",
            "outcome": "FAIL"
        }

    answer = match.group(1).strip()
    # Remove inline citation artifacts like 【1】【Barclays】【Annual Report 2024】【46–47】
    answer = re.sub(r"【[^】]+】", "", answer).strip()

    sources = []
    seen = set()
    for match in re.finditer(
        r'"source_id"\s*:\s*(\d+).*?"company"\s*:\s*"([^"]+)".*?"document"\s*:\s*"([^"]+)".*?"pages"\s*:\s*"([^"]+)"',
        evidence_context,
        re.DOTALL | re.IGNORECASE
    ):
        source_id, company, document, pages = match.groups()
        key = (source_id, company, document, pages)
        if key not in seen:
            seen.add(key)
            sources.append(
                f"SOURCE [{source_id}] — {company}, {document}, Pages {pages}"
            )

    if not answer or len(answer) < 20:
        return {
            "answer": "I do not have enough information in the provided documents.",
            "outcome": "FAIL"
        }

    return {
        "answer": answer,
        "sources": sources,
        "outcome": "PASS"
    }