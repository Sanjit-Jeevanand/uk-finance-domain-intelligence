"""
Chunk extracted annual report text into retrieval-ready chunks
with full traceability metadata.
"""

from pathlib import Path
import json
import re
from typing import List, Dict

# -----------------------------
# Config (tune later if needed)
# -----------------------------

TARGET_CHARS = 4000        # ~800–1000 tokens depending on text
OVERLAP_CHARS = 500
PAGE_MARKER_PATTERN = re.compile(r"\[PAGE (\d+)\]")


# -----------------------------
# Helpers
# -----------------------------

def load_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Text file not found: {path}")
    return path.read_text(encoding="utf-8")


def load_metadata(path: Path) -> Dict:
    if not path.exists():
        raise FileNotFoundError(f"Metadata file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def split_by_pages(text: str) -> List[Dict]:
    """
    Split document text into page-level blocks.
    Returns list of:
    {
        "page_number": int,
        "text": str
    }
    """
    matches = list(PAGE_MARKER_PATTERN.finditer(text))

    if not matches:
        # Fallback: no page markers
        return [{
            "page_number": None,
            "text": text.strip()
        }]

    pages = []

    for i, match in enumerate(matches):
        page_number = int(match.group(1))
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)

        page_text = text[start:end].strip()
        if page_text:
            pages.append({
                "page_number": page_number,
                "text": page_text
            })

    return pages


# -----------------------------
# Core chunking logic
# -----------------------------

def chunk_pages(
    pages: List[Dict],
    document_metadata: Dict
) -> List[Dict]:
    """
    Convert page-level text into overlapping chunks
    while preserving page traceability.
    """
    chunks = []

    buffer = ""
    buffer_pages = []

    chunk_index = 0

    for page in pages:
        page_text = page["text"]
        page_number = page["page_number"]

        buffer += "\n" + page_text
        buffer_pages.append(page_number)

        if len(buffer) >= TARGET_CHARS:
            chunk = build_chunk(
                buffer,
                buffer_pages,
                document_metadata,
                chunk_index
            )
            chunks.append(chunk)

            # overlap handling
            buffer = buffer[-OVERLAP_CHARS:]
            buffer_pages = buffer_pages[-1:]

            chunk_index += 1

    # flush remainder
    if buffer.strip():
        chunk = build_chunk(
            buffer,
            buffer_pages,
            document_metadata,
            chunk_index
        )
        chunks.append(chunk)

    return chunks


def build_chunk(
    text: str,
    pages: List[int],
    document_metadata: Dict,
    chunk_index: int
) -> Dict:
    """
    Construct a single chunk with full metadata.
    """
    page_numbers = [p for p in pages if p is not None]

    return {
        "chunk_id": f"{document_metadata['company']}_{document_metadata['fiscal_year']}_{chunk_index}",
        "chunk_index": chunk_index,
        "text": text.strip(),

        # traceability
        "page_start": min(page_numbers) if page_numbers else None,
        "page_end": max(page_numbers) if page_numbers else None,

        # inherited document metadata
        **document_metadata
    }


# -----------------------------
# Public entrypoint
# -----------------------------

def chunk_document(
    text_path: Path,
    metadata_path: Path,
    output_path: Path
) -> None:
    """
    Chunk a single document and write chunks as JSONL.
    """
    text = load_text(text_path)
    metadata = load_metadata(metadata_path)

    pages = split_by_pages(text)
    chunks = chunk_pages(pages, metadata)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(json.dumps(chunk) + "\n")

    print(f"Created {len(chunks)} chunks → {output_path}")

if __name__ == "__main__":
    from pathlib import Path

    BASE_DIR = Path("data")

    TEXT_DIR = BASE_DIR / "processed" / "clean_text" / "annual_reports"
    META_DIR = BASE_DIR / "processed" / "metadata" / "annual_reports"
    OUTPUT_DIR = BASE_DIR / "chunks" / "annual_reports"

    for company_dir in TEXT_DIR.iterdir():
        for year_dir in company_dir.iterdir():
            text_file = year_dir / f"{company_dir.name}_{year_dir.name}_annual_report.txt"
            meta_dir = META_DIR / company_dir.name / year_dir.name
            meta_files = list(meta_dir.glob("*.json"))

            if len(meta_files) != 1:
                print(f"Skipping {company_dir.name} {year_dir.name} (expected 1 metadata file, found {len(meta_files)})")
                continue

            meta_file = meta_files[0]
            output_file = OUTPUT_DIR / company_dir.name / year_dir.name / "chunks.jsonl"

            if not text_file.exists() or not meta_file.exists():
                print(f"Skipping {company_dir.name} {year_dir.name}")
                continue

            chunk_document(
                text_path=text_file,
                metadata_path=meta_file,
                output_path=output_file
            )