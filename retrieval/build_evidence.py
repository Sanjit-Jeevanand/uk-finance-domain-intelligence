def build_evidence_context(chunks, max_chars=3500):
    """
    Takes filtered chunks and builds a grounded evidence context
    suitable for LLM prompting.
    """
    context = []
    total_chars = 0

    for i, c in enumerate(chunks, start=1):
        block = f"""
SOURCE [{i}]
Company: {c['company']}
Document: {c['report_type'].replace('_', ' ').title()} {c['fiscal_year']}
Pages: {c['page_start']}–{c['page_end']}
Content:
\"\"\"
{c['text'].strip()}
\"\"\"
""".strip()

        if total_chars > 0 and total_chars + len(block) > max_chars:
            break

        context.append(block)
        total_chars += len(block)

    return "\n\n".join(context)