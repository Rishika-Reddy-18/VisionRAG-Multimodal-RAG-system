

from rag.chunking import chunk_text

from rag.vector_store import add_to_vector_db


def clean_text(text):

    if not text:
        return ""

    text = text.strip()

    if len(text) < 10:
        return ""

    return text


def process_text(text):

    print("STEP 1: PROCESS STARTED")

    text = clean_text(text)

    print("STEP 2: CLEAN TEXT DONE")

    if not text:
        print("ERROR: EMPTY TEXT")
        return

    print("TEXT LENGTH:", len(text))

    chunks = chunk_text(text)

    print("STEP 3: CHUNKING DONE")

    if not chunks:
        print("ERROR: NO CHUNKS")
        return

    print("NUMBER OF CHUNKS:", len(chunks))

    print("STEP 4: EMBEDDING MODEL LOADED")

    add_to_vector_db(chunks)

    print("STEP 5: VECTOR DB SAVED")