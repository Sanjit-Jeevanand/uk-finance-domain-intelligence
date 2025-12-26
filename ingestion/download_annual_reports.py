"""
UK Finance Domain Intelligence System
Phase 1 — Annual Report Ingestion

Responsibilities (eventual):
- Read data source registry (YAML)
- Download annual reports
- Store raw documents
- Extract clean text
- Prepare for downstream processing
"""

from pathlib import Path
import logging
from typing import Dict, List
import yaml
import requests
from ingestion.metadata import build_document_metadata

# -----------------------------
# Configuration
# -----------------------------

DATA_SOURCES_DIR = Path("data_sources")
RAW_DATA_DIR = Path("data/raw")
PROCESSED_DATA_DIR = Path("data/processed")

ANNUAL_REPORTS_YAML = DATA_SOURCES_DIR / "annual_reports.yaml"
RAW_ANNUAL_REPORTS_DIR = RAW_DATA_DIR / "annual_reports"
PROCESSED_TEXT_DIR = PROCESSED_DATA_DIR / "text" / "annual_reports"
METADATA_DIR = PROCESSED_DATA_DIR / "metadata" / "annual_reports"

# -----------------------------
# Logging
# -----------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

# -----------------------------
# Core Interfaces
# -----------------------------

def load_data_sources(yaml_path: Path) -> List[Dict]:
    """
    Load and validate data source definitions.

    Args:
        yaml_path: Path to YAML registry

    Returns:
        List of document source definitions
    """
    if not yaml_path.exists():
        raise FileNotFoundError(
            f"Data source registry not found at: {yaml_path}"
        )

    with yaml_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, list):
        raise ValueError(
            "Data source registry must be a list of source definitions"
        )

    required_keys = {
        "company",
        "ticker",
        "fiscal_year",
        "report_type",
        "url",
    }

    validated_sources: List[Dict] = []

    for idx, entry in enumerate(data):
        if not isinstance(entry, dict):
            raise ValueError(
                f"Entry {idx} is not a dictionary: {entry}"
            )

        missing = required_keys - entry.keys()
        if missing:
            raise ValueError(
                f"Entry {idx} missing required fields: {missing}"
            )

        # Semantic validation (lightweight, fail-fast)
        if not isinstance(entry["url"], str) or not entry["url"].startswith("http"):
            raise ValueError(
                f"Entry {idx} has invalid url: {entry['url']}"
            )

        if not isinstance(entry["fiscal_year"], int) or not (2020 <= entry["fiscal_year"] <= 2024):
            raise ValueError(
                f"Entry {idx} has invalid fiscal_year: {entry['fiscal_year']}"
            )

        if entry["report_type"] != "annual_report":
            raise ValueError(
                f"Entry {idx} has unsupported report_type: {entry['report_type']}"
            )

        if any(sep in entry["company"] for sep in ["/", "\\"]):
            raise ValueError(
                f"Entry {idx} has unsafe company name: {entry['company']}"
            )

        validated_sources.append(entry)

    logger.info(
        f"Loaded {len(validated_sources)} annual report source(s)"
    )

    return validated_sources


def download_annual_report(source: Dict) -> Path:
    """
    Download a single annual report PDF.

    Args:
        source: Data source metadata

    Returns:
        Path to downloaded PDF
    """
    company = source["company"]
    fiscal_year = source["fiscal_year"]
    url = source["url"]

    output_dir = RAW_ANNUAL_REPORTS_DIR / company / str(fiscal_year)
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{company}_{fiscal_year}_annual_report.pdf"
    output_path = output_dir / filename

    if output_path.exists():
        logger.info(f"File already exists, skipping download: {output_path}")
        return output_path

    logger.info(f"Downloading annual report from {url} to {output_path}")
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "application/pdf",
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to download {url}: {e}")

    with open(output_path, "wb") as f:
        f.write(response.content)

    logger.info(f"Downloaded and saved annual report: {output_path}")
    return output_path


def extract_text_from_pdf(pdf_path: Path, output_dir: Path, source: Dict) -> Path:
    """
    Extract raw text from a PDF using pdfplumber.

    Args:
        pdf_path: Path to PDF
        output_dir: Base directory to write extracted text
        source: Data source metadata

    Returns:
        Path to extracted text file
    """
    import pdfplumber

    company = pdf_path.parent.parent.name
    fiscal_year = pdf_path.parent.name

    output_path = (
        output_dir
        / company
        / fiscal_year
        / pdf_path.with_suffix(".txt").name
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    metadata = build_document_metadata(
        company=source["company"],
        ticker=source["ticker"],
        sector=source.get("sector"),
        country=source.get("country"),
        fiscal_year=source["fiscal_year"],
        report_type=source["report_type"],
        source_url=source["url"],
        raw_pdf_path=str(pdf_path),
        extracted_text_path=str(output_path),
    )

    if output_path.exists():
        logger.info(f"Text already extracted, skipping: {output_path}")
    else:
        logger.info(f"Extracting text from PDF: {pdf_path}")

        extracted_pages = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    text = page.extract_text() or ""
                    extracted_pages.append(
                        f"\n--- PAGE {page_num} ---\n{text}"
                    )
        except Exception as e:
            raise RuntimeError(f"Failed to extract text from {pdf_path}: {e}")

        with output_path.open("w", encoding="utf-8") as f:
            f.write("\n".join(extracted_pages))

    metadata_path = (
        METADATA_DIR
        / source["company"]
        / str(source["fiscal_year"])
        / pdf_path.with_suffix(".json").name
    )
    metadata_path.parent.mkdir(parents=True, exist_ok=True)

    if not metadata_path.exists():
        import json
        with metadata_path.open("w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Metadata saved to: {metadata_path}")
    else:
        logger.info(f"Metadata already exists, skipping: {metadata_path}")

    return output_path


# -----------------------------
# Pipeline Orchestration
# -----------------------------

def download_annual_reports():
    """
    Download annual report PDFs defined in data_sources.
    """
    logger.info("Starting annual report ingestion pipeline")

    # 1. Load registry
    sources = load_data_sources(ANNUAL_REPORTS_YAML)

    # 2. Iterate through sources
    for source in sources:
        logger.info(
            f"Ingesting {source['company']} "
            f"({source['fiscal_year']})"
        )

        # 3. Download
        pdf_path = download_annual_report(source)

        # 4. Extract text
        extract_text_from_pdf(
            pdf_path=pdf_path,
            output_dir=PROCESSED_TEXT_DIR,
            source=source
        )

    logger.info("Ingestion pipeline completed")


# -----------------------------
# Entry Point
# -----------------------------

if __name__ == "__main__":
    download_annual_reports()