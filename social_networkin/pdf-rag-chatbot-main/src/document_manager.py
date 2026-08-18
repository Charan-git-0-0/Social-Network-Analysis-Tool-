from pathlib import Path

from src.config import UPLOAD_DIR, ensure_data_dirs
from src.vector_store import rebuild_vector_store


def get_uploaded_documents():
    ensure_data_dirs()
    return sorted(UPLOAD_DIR.glob("*.pdf"))


def save_uploaded_files(uploaded_files):
    ensure_data_dirs()
    saved_paths = []

    for uploaded_file in uploaded_files:
        safe_name = Path(uploaded_file.name).name
        destination = UPLOAD_DIR / safe_name
        destination.write_bytes(uploaded_file.getbuffer())
        saved_paths.append(destination)

    return saved_paths


def delete_document(filename):
    ensure_data_dirs()
    target = UPLOAD_DIR / Path(filename).name

    if target.exists():
        target.unlink()

    rebuild_vector_store()
