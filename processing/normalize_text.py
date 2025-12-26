"""
Phase 1 — Text Normalization
Purpose:
- Light cleanup of extracted PDF text
- Preserve semantics for RAG
"""

from pathlib import Path
import logging
import re

# -----------------------------
# Configuration
# -----------------------------

INPUT_DIR = Path("data/processed/text/annual_reports")
OUTPUT_DIR = Path("data/processed/clean_text/annual_reports")

# -----------------------------
# Logging
# -----------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

# -----------------------------
# Normalization Rules
# -----------------------------

PAGE_MARKER_PATTERN = re.compile(r"-{3}\s*PAGE\s*(\d+)\s*-{3}", re.IGNORECASE)

HEADER_FOOTER_PATTERNS = [
    re.compile(r"^.*annual report.*$", re.IGNORECASE),
    re.compile(r"^.*©.*$", re.IGNORECASE),
]

def normalize_text(raw_text: str) -> str:
    """
    Apply conservative normalization rules.
    """

    # Normalize page markers
    text = PAGE_MARKER_PATTERN.sub(r"\n[PAGE \1]\n", raw_text)

    lines = text.splitlines()
    cleaned_lines = []

    for line in lines:
        stripped = line.strip()

        # Skip empty junk
        if not stripped:
            cleaned_lines.append("")
            continue

        # Remove obvious headers / footers
        if any(p.match(stripped) for p in HEADER_FOOTER_PATTERNS):
            continue

        cleaned_lines.append(stripped)

    text = "\n".join(cleaned_lines)

    # Normalize excessive newlines (max 2)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


# -----------------------------
# Pipeline
# -----------------------------

def normalize_all_reports():
    logger.info("Starting text normalization")

    for txt_path in INPUT_DIR.rglob("*.txt"):
        relative_path = txt_path.relative_to(INPUT_DIR)
        output_path = OUTPUT_DIR / relative_path

        output_path.parent.mkdir(parents=True, exist_ok=True)

        if output_path.exists():
            logger.info(f"Skipping already normalized file: {output_path}")
            continue

        logger.info(f"Normalizing: {txt_path}")

        raw_text = txt_path.read_text(encoding="utf-8", errors="ignore")
        cleaned_text = normalize_text(raw_text)

        output_path.write_text(cleaned_text, encoding="utf-8")

    logger.info("Text normalization completed")


# -----------------------------
# Entry Point
# -----------------------------

if __name__ == "__main__":
    normalize_all_reports()