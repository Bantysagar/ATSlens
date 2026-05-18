from io import BytesIO

from docx import Document
from fastapi import UploadFile
from pypdf import PdfReader


async def extract_text_from_resume(file: UploadFile) -> str:
    filename = file.filename.lower()
    content = await file.read()

    if filename.endswith(".pdf"):
        return extract_pdf_text(content)

    if filename.endswith(".docx"):
        return extract_docx_text(content)

    if filename.endswith(".txt"):
        return extract_txt_text(content)

    raise ValueError("Unsupported file type. Please upload PDF, DOCX, or TXT.")


def extract_pdf_text(content: bytes) -> str:
    text = ""

    reader = PdfReader(BytesIO(content))

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return text.strip()


def extract_docx_text(content: bytes) -> str:
    text = ""

    document = Document(BytesIO(content))

    for paragraph in document.paragraphs:
        if paragraph.text:
            text += paragraph.text + "\n"

    return text.strip()


def extract_txt_text(content: bytes) -> str:
    try:
        return content.decode("utf-8").strip()
    except UnicodeDecodeError:
        return content.decode("latin-1").strip()