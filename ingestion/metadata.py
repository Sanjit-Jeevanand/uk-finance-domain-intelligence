from pathlib import Path
from typing import Dict


def build_document_metadata(
    *,
    company: str,
    ticker: str,
    sector: str,
    country: str,
    fiscal_year: int,
    report_type: str,
    source_url: str,
    raw_pdf_path: Path,
    extracted_text_path: Path,
) -> Dict:
    """
    Build canonical document-level metadata for a financial report.

    This metadata is attached ONCE per document and inherited by all chunks.

    Returns:
        dict: Document metadata
    """

    return {
        # Identity
        "company": company,
        "ticker": ticker,
        "sector": sector,
        "country": country,

        # Document classification
        "report_type": report_type,
        "fiscal_year": fiscal_year,

        # Provenance
        "source_url": source_url,
        "raw_pdf_path": str(raw_pdf_path),
        "extracted_text_path": str(extracted_text_path),

        # System bookkeeping
        "document_id": f"{company}_{fiscal_year}_{report_type}",
    }