from pathlib import Path
import json
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import numpy as np

CHUNKS_DIR = Path("data/chunks/annual_reports")
OUTPUT_DIR = Path("data/embeddings")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

def load_chunks():
    chunks = []
    for company_dir in CHUNKS_DIR.iterdir():
        for year_dir in company_dir.iterdir():
            chunks_file = year_dir / "chunks.jsonl"
            if not chunks_file.exists():
                continue

            with open(chunks_file, "r") as f:
                for line in f:
                    chunks.append(json.loads(line))
    return chunks

def main():
    model = SentenceTransformer(MODEL_NAME)

    chunks = load_chunks()
    texts = [c["text"] for c in chunks]

    print(f"Embedding {len(texts)} chunks…")

    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True,
        normalize_embeddings=True
    )

    np.save(OUTPUT_DIR / "embeddings.npy", embeddings)

    with open(OUTPUT_DIR / "metadata.json", "w") as f:
        json.dump(chunks, f, indent=2)

    print("Embeddings and metadata saved")

if __name__ == "__main__":
    main()