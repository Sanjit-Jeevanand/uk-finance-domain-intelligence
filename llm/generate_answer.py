import subprocess
import os
from typing import Dict
import re
import hashlib
import json
from pathlib import Path
import requests
from openai import OpenAI

SYSTEM_PROMPT = """You are a financial analysis assistant answering questions over official company reports.

Your task:
- Answer the USER QUESTION using ONLY the information in the CONTEXT.
- The CONTEXT consists of extracted excerpts from financial documents.

Interpretation guidance:
- You may internally rephrase or restate the USER QUESTION to better match the structure and wording of the CONTEXT.
- Rephrasing is permitted ONLY to improve alignment with how information is described in the source documents.
- You must NOT broaden the scope of the question, introduce new concepts, or infer intent beyond what is explicitly stated.
- The final answer must still be strictly grounded in the CONTEXT.

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
- If the context contains sufficient information from the same company, document, and fiscal year, you SHOULD answer by summarising the relevant excerpts. Only refuse if the information is genuinely missing.
- If the context contains relevant information that partially answers the question, provide a concise, evidence-grounded summary. Only refuse if the context is clearly irrelevant or empty.
- You MUST preserve modal language exactly as written in the context.
  If the source uses terms such as "could", "may", or "might", you MUST NOT
  restate them as definitive outcomes (e.g. "will", "does", "has").

Exception (controlled):
- You MAY summarise across multiple excerpts IF:
  - All excerpts are from the SAME company
  - All excerpts are from the SAME document
  - All excerpts are from the SAME fiscal year

---

<SOURCES>
SOURCE [X] — Company, Document, Fiscal Year, Pages A–B
"""

CACHE_DIR = Path(".llm_cache")
CACHE_DIR.mkdir(exist_ok=True)

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
client = OpenAI()

def _prompt_hash(prompt: str) -> str:
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()


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
    model: str = OPENAI_MODEL,
) -> Dict:
    """
    Generate a grounded answer using a local LLM.

    Returns:
    {
        "answer": str,
        "raw_output": str
    }
    """
    refusal_string = "I do not have enough information in the provided documents."

    if not evidence_context.strip():
        return {
            "answer": refusal_string
        }

    prompt = build_prompt(question, evidence_context)

    cache_payload = json.dumps(
        {
            "prompt": prompt,
            "model": model,
            "options": {
                "temperature": 0,
                "top_p": 1,
                "repeat_penalty": 1,
            },
        },
        sort_keys=True,
    )

    cache_key = hashlib.sha256(cache_payload.encode("utf-8")).hexdigest()
    cache_path = CACHE_DIR / f"{cache_key}.json"

    if cache_path.exists():
        cached_result = json.loads(cache_path.read_text())
        cached_answer = cached_result.get("answer", "")
        # Bypass cache if cached answer is refusal but evidence_context is large enough
        if cached_answer == refusal_string and len(evidence_context.strip()) >= 400:
            pass  # recompute instead of returning cache
        else:
            return cached_result

    response = client.responses.create(
        model=model,
        input=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": f"CONTEXT:\n{evidence_context}\n\nQUESTION:\n{question}"
            }
        ],
        temperature=0,
        max_output_tokens=600
    )

    output_text = response.output_text

    if output_text.strip() == refusal_string:
        answer = refusal_string
    else:
        answer = output_text.strip()

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

    if not answer:
        answer = refusal_string

    result = {
        "answer": answer,
        "sources": sources
    }

    cache_path.write_text(json.dumps(result, indent=2))
    return result