from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import CHUNK_OVERLAP, CHUNK_SIZE


def split_pages_into_chunks(pages):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    texts = []
    metadatas = []

    for page in pages:
        chunks = splitter.split_text(page["text"])

        for chunk_index, chunk in enumerate(chunks):
            metadata = dict(page["metadata"])
            metadata["chunk"] = chunk_index
            texts.append(chunk)
            metadatas.append(metadata)

    return texts, metadatas
