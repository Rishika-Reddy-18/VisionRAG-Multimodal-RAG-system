from rag.vector_store import load_vector_db


def retrieve(query):

    db = load_vector_db()

    docs = db.similarity_search(query, k=3)

    return docs