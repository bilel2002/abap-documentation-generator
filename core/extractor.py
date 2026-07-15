# core/extractor.py

import fitz  # pymupdf
from pathlib import Path


def extract_text(file):


    # Normalize filename
    filename = getattr(file, "name", str(file)).lower()

    # ---------- TEXT / ABAP FILE ----------
    if filename.endswith((".txt", ".abap")):
        return _read_text_file(file)

    # ---------- PDF FILE ----------
    if filename.endswith(".pdf"):
        return _read_pdf(file)

    raise ValueError("Unsupported file type. Only PDF, TXT, ABAP allowed.")


def _read_text_file(file):
    """
    Read TXT or ABAP file safely.
    """

    if hasattr(file, "read"):
        try:
            return file.read().decode("utf-8", errors="ignore")
        except Exception:
            return file.read()

    # local file path
    with open(file, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def _read_pdf(file):
    """
    Extract text from PDF using PyMuPDF.
    """

    if hasattr(file, "read"):
        doc = fitz.open(stream=file.read(), filetype="pdf")
    else:
        doc = fitz.open(file)

    pages_text = []

    for page in doc:
        text = page.get_text()
        if text:
            pages_text.append(text)

    return "\n".join(pages_text)


def get_file_info(file):
    return {
        "name": getattr(file, "name", None),
        "type": getattr(file, "type", None),
        "size": getattr(file, "size", None),
    }