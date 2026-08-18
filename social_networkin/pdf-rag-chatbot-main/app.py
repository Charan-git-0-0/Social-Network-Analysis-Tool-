import streamlit as st

from src.chat_history import add_message, initialize_chat_history, render_chat_history
from src.config import validate_google_api_key
from src.document_manager import delete_document, get_uploaded_documents, save_uploaded_files
from src.rag_chain import answer_question
from src.vector_store import add_pdfs_to_vector_store, get_collection_count


def render_sidebar():
    st.sidebar.title("Documents")

    uploaded_files = st.sidebar.file_uploader(
        "Upload PDF files",
        type=["pdf"],
        accept_multiple_files=True,
    )

    if st.sidebar.button("Process uploads", type="primary"):
        if not uploaded_files:
            st.sidebar.warning("Upload at least one PDF first.")
        else:
            with st.spinner("Reading PDFs and storing chunks in ChromaDB..."):
                saved_paths = save_uploaded_files(uploaded_files)
                added_chunks = add_pdfs_to_vector_store(saved_paths)
            st.sidebar.success(f"Added {added_chunks} chunks.")

    st.sidebar.divider()
    st.sidebar.subheader("Library")

    documents = get_uploaded_documents()
    if not documents:
        st.sidebar.caption("No PDFs uploaded yet.")

    for document in documents:
        col1, col2 = st.sidebar.columns([4, 1])
        col1.caption(document.name)
        if col2.button("Delete", key=f"delete-{document.name}"):
            with st.spinner(f"Deleting {document.name}..."):
                delete_document(document.name)
            st.rerun()

    st.sidebar.divider()
    st.sidebar.caption(f"Stored chunks: {get_collection_count()}")


def main():
    st.set_page_config(page_title="PDF RAG Chatbot")
    st.title("PDF RAG Chatbot")

    initialize_chat_history()
    missing_key_message = validate_google_api_key()
    if missing_key_message:
        st.error(missing_key_message)
        st.stop()

    render_sidebar()
    render_chat_history()

    user_question = st.chat_input("Ask a question about your PDFs")
    if not user_question:
        return

    add_message("user", user_question)
    with st.chat_message("user"):
        st.write(user_question)

    with st.chat_message("assistant"):
        with st.spinner("Retrieving relevant chunks and generating answer..."):
            result = answer_question(user_question)

        st.write(result["answer"])

        if result["sources"]:
            st.markdown("**Sources**")
            for source in result["sources"]:
                st.caption(f"{source['source']} - page {source['page']}")

        with st.expander("Retrieved context"):
            for index, chunk in enumerate(result["retrieved_chunks"], start=1):
                st.markdown(f"**Chunk {index}: {chunk['source']} - page {chunk['page']}**")
                st.write(chunk["text"])

    add_message(
        "assistant",
        result["answer"],
        sources=result["sources"],
        retrieved_chunks=result["retrieved_chunks"],
    )


if __name__ == "__main__":
    main()
