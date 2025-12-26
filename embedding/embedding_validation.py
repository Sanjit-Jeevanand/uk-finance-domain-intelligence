import json
import numpy as np
from pathlib import Path

EMB_DIR = Path("data/embeddings")

embeddings = np.load(EMB_DIR / "embeddings.npy")
with open(EMB_DIR / "metadata.json") as f:
    metadata = json.load(f)

print("Embeddings shape:", embeddings.shape)
print("Metadata entries:", len(metadata))

norms = np.linalg.norm(embeddings, axis=1)

print("Min norm:", norms.min())
print("Max norm:", norms.max())
print("Mean norm:", norms.mean())

from sklearn.metrics.pairwise import cosine_similarity

i, j = 10, 11  # adjacent chunks from same doc
k = 200       # random far-away chunk

sim_close = cosine_similarity(
    embeddings[i].reshape(1, -1),
    embeddings[j].reshape(1, -1)
)[0][0]

sim_far = cosine_similarity(
    embeddings[i].reshape(1, -1),
    embeddings[k].reshape(1, -1)
)[0][0]

print("Similar chunks similarity:", sim_close)
print("Distant chunks similarity:", sim_far)

print(metadata[0])