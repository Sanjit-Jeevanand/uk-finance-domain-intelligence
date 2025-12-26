import json
import faiss
import numpy as np
from pathlib import Path

INDEX_PATH = Path("data/embeddings/faiss.index")
METADATA_PATH = Path("data/embeddings/metadata.json")

def load_faiss():
    index = faiss.read_index(str(INDEX_PATH))
    with open(METADATA_PATH, "r") as f:
        metadata = json.load(f)
    return index, metadata


def search(index, metadata, query_embedding, top_k=5):
    if query_embedding.ndim == 1:
        query_embedding = query_embedding.reshape(1, -1)

    scores, indices = index.search(query_embedding, top_k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        entry = metadata[idx].copy()
        entry["score"] = float(score)
        results.append(entry)

    return results