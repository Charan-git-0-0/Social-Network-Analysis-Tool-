# PDF RAG Chatbot

A Streamlit PDF chatbot that uses Gemini for embeddings and answering, with ChromaDB as the persistent vector database.

## RAG Flow

1. Upload PDF documents.
2. Extract text from each page.
3. Split text into chunks.
4. Create embeddings for each chunk.
5. Store chunks, embeddings, PDF name, and page number in ChromaDB.
6. Ask a question.
7. Retrieve relevant chunks from ChromaDB.
8. Send retrieved context plus the question to Gemini.
9. Display the answer with source citations.

## Setup

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file:

```env
GOOGLE_API_KEY=your_google_api_key_here
```

Run the app:

```powershell
streamlit run app.py
```

## Project Structure

```text
app.py
src/
  chat_history.py
  config.py
  document_manager.py
  pdf_loader.py
  rag_chain.py
  text_splitter.py
  vector_store.py
data/
  uploads/
  chroma_db/
```
