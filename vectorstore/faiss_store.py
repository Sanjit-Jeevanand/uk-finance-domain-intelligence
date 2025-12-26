from pathlib import Path
import faiss
import numpy as np
import json

INDEX_PATH = Path("data/embeddings/faiss.index")
METADATA_PATH = Path("data/embeddings/metadata.json")

class FAISSVectorStore:
    def __init__(self):
        self.index = faiss.read_index(str(INDEX_PATH))
        with open(METADATA_PATH, "r") as f:
            self.metadata = json.load(f)

    def search(self, query_embedding: np.ndarray, top_k: int = 5):
        query_embedding = query_embedding.astype("float32").reshape(1, -1)

        scores, indices = self.index.search(query_embedding, top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            item = self.metadata[idx]
            item["score"] = float(score)
            results.append(item)

        return results