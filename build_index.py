import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

texts = [
    "VisionRAG system",
    "Multimodal AI project",
    "Uses FAISS for retrieval"
]

embeddings = model.encode(texts)

index = faiss.IndexFlatL2(len(embeddings[0]))
index.add(np.array(embeddings).astype("float32"))

faiss.write_index(index, "models/vector_db/faiss.index")

with open("models/vector_db/texts.pkl", "wb") as f:
    pickle.dump(texts, f)

print("Index created")