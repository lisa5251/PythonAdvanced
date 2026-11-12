
import pymupdf
from docx import Document
from io import BytesIO


def extract_pdf_text(file_bytes: bytes) -> str:
    """Extract text from a PDF resume."""

    document = pymupdf.open(
        stream=file_bytes,
        filetype="pdf"
    )

    try:
        text = ""

        for page in document:
            text += page.get_text() + "\n"

        return text.strip()

    finally:
        document.close()


def extract_docx_text(file_bytes: bytes) -> str:
    """Extract text from a Word document."""

    document = Document(BytesIO(file_bytes))

    paragraphs = [
        paragraph.text
        for paragraph in document.paragraphs
    ]

    # Also extract text from tables
    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                paragraphs.append(cell.text)

    return "\n".join(paragraphs).strip()


def extract_resume_text(filename: str, file_bytes: bytes) -> str:
    """Detect file format and extract resume text."""

    filename = filename.lower()

    if filename.endswith(".pdf"):
        return extract_pdf_text(file_bytes)

    elif filename.endswith(".docx"):
        return extract_docx_text(file_bytes)

    else:
        raise ValueError(
            "Only PDF and DOCX files are supported"
        )
