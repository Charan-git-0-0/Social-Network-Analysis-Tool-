from langchain_google_genai import ChatGoogleGenerativeAI

from src.config import RETRIEVAL_K
from src.vector_store import search_relevant_chunks


PROMPT_TEMPLATE = """
You are a careful PDF research assistant.

Use only the provided context to answer the question.
If the answer is not available in the context, say:
"The answer is not available in the uploaded documents."

Context:
{context}

Question:
{question}

Answer:
"""


def _format_context(chunks):
    formatted_chunks = []

    for chunk in chunks:
        formatted_chunks.append(
            f"Source: {chunk['source']}, page {chunk['page']}\n{chunk['text']}"
        )

    return "\n\n---\n\n".join(formatted_chunks)


def _unique_sources(chunks):
    seen = set()
    sources = []

    for chunk in chunks:
        key = (chunk["source"], chunk["page"])
        if key in seen:
            continue

        seen.add(key)
        sources.append({"source": chunk["source"], "page": chunk["page"]})

    return sources


def answer_question(question):
    chunks = search_relevant_chunks(question, k=RETRIEVAL_K)

    if not chunks:
        return {
            "answer": "Upload and process at least one PDF before asking questions.",
            "sources": [],
            "retrieved_chunks": [],
        }

    model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)
    final_prompt = PROMPT_TEMPLATE.format(
        context=_format_context(chunks),
        question=question,
    )
    response = model.invoke(final_prompt)

    return {
        "answer": response.content,
        "sources": _unique_sources(chunks),
        "retrieved_chunks": chunks,
    }
