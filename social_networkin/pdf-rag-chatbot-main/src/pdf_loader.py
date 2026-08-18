from PyPDF2 import PdfReader


def load_pdf_pages(pdf_path):
    reader = PdfReader(str(pdf_path))
    pages = []

    for page_index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        text = text.strip()

        if text:
            pages.append(
                {
                    "text": text,
                    "metadata": {
                        "source": pdf_path.name,
                        "page": page_index,
                    },
                }
            )

    return pages
