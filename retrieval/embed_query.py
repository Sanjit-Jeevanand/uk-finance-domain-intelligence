from sentence_transformers import SentenceTransformer
import numpy as np

class QueryEmbedder:
    def __init__(self, model_name: str):
        self.model = SentenceTransformer(model_name)

    def embed(self, query: str) -> np.ndarray:
        """
        Embed a single query into the same vector space as document chunks.
        """
        embedding = self.model.encode(
            query,
            normalize_embeddings=True
        )

        return embedding