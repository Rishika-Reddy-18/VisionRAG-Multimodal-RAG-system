from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

import os
import shutil

DB_FAISS_PATH = "models/vector_db"

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

def add_to_vector_db(chunks):

    db = FAISS.from_texts(
        texts=chunks,
        embedding=embedding_model
    )

    os.makedirs(DB_FAISS_PATH, exist_ok=True)

    db.save_local(DB_FAISS_PATH)

    print("FAISS SAVED SUCCESSFULLY")


def load_vector_db():

    faiss_file = os.path.join(
        DB_FAISS_PATH,
        "index.faiss"
    )

    if not os.path.exists(faiss_file):
        raise FileNotFoundError("FAISS index not found")

    db = FAISS.load_local(
        DB_FAISS_PATH,
        embedding_model,
        allow_dangerous_deserialization=True
    )

    return db


def clear_vector_db():

    if os.path.exists(DB_FAISS_PATH):

        shutil.rmtree(DB_FAISS_PATH)

        print("VECTOR DB CLEARED")