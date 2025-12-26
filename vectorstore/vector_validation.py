from sentence_transformers import SentenceTransformer
from vectorstore.faiss_store import FAISSVectorStore

model = SentenceTransformer("all-MiniLM-L6-v2")
store = FAISSVectorStore()

query = "What risks does Barclays face in 2024?"
q_emb = model.encode(query, normalize_embeddings=True)

results = store.search(q_emb, top_k=5)

for r in results:
    print(r["score"], r["company"], r["page_start"], r["page_end"])