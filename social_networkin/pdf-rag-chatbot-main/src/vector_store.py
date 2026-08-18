import uuid

import chromadb
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from src.config import CHROMA_DIR, COLLECTION_NAME, UPLOAD_DIR, ensure_data_dirs
from src.pdf_loader import load_pdf_pages
from src.text_splitter import split_pages_into_chunks


def get_embedding_model():
    return GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")


def get_chroma_client():
    ensure_data_dirs()
    return chromadb.PersistentClient(path=str(CHROMA_DIR))


def get_collection():
    client = get_chroma_client()
    return client.get_or_create_collection(name=COLLECTION_NAME)


def get_collection_count():
    return get_collection().count()


def add_pdfs_to_vector_store(pdf_paths):
    collection = get_collection()
    embeddings = get_embedding_model()
    total_chunks = 0

    for pdf_path in pdf_paths:
        collection.delete(where={"source": pdf_path.name})
        pages = load_pdf_pages(pdf_path)
        texts, metadatas = split_pages_into_chunks(pages)

        if not texts:
            continue

        ids = [
            f"{pdf_path.stem}-{metadata['page']}-{metadata['chunk']}-{uuid.uuid4().hex}"
            for metadata in metadatas
        ]
        vectors = embeddings.embed_documents(texts)

        collection.add(
            ids=ids,
            documents=texts,
            embeddings=vectors,
            metadatas=metadatas,
        )
        total_chunks += len(texts)

    return total_chunks


def search_relevant_chunks(question, k=4):
    collection = get_collection()

    if collection.count() == 0:
        return []

    embeddings = get_embedding_model()
    query_embedding = embeddings.embed_query(question)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(k, collection.count()),
    )

    chunks = []
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for document, metadata, distance in zip(documents, metadatas, distances):
        chunks.append(
            {
                "text": document,
                "source": metadata["source"],
                "page": metadata["page"],
                "distance": distance,
            }
        )

    return chunks


def rebuild_vector_store():
    ensure_data_dirs()
    client = get_chroma_client()

    try:
        client.delete_collection(name=COLLECTION_NAME)
    except ValueError:
        pass

    remaining_pdfs = sorted(UPLOAD_DIR.glob("*.pdf"))

    if remaining_pdfs:
        add_pdfs_to_vector_store(remaining_pdfs)
