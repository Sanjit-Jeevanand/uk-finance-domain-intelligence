from pathlib import Path
import numpy as np
import faiss
import json

EMBEDDINGS_PATH = Path("data/embeddings/embeddings.npy")
METADATA_PATH = Path("data/embeddings/metadata.json")
INDEX_PATH = Path("data/embeddings/faiss.index")

def build_faiss_index():
    embeddings = np.load(EMBEDDINGS_PATH).astype("float32")

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)

    index.add(embeddings)

    faiss.write_index(index, str(INDEX_PATH))

    print(f"FAISS index built")
    print(f"Vectors indexed: {index.ntotal}")
    print(f"Embedding dimension: {dim}")
    print(f"Saved to: {INDEX_PATH}")

if __name__ == "__main__":
    build_faiss_index()