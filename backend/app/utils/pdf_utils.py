import os
import re
from typing import Optional, Tuple

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False


def extract_text_from_pdf(file_path: str) -> Tuple[str, int]:
    """Extract text content and page count from a PDF file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    if not PDFPLUMBER_AVAILABLE:
        return _extract_text_fallback(file_path)

    text_parts = []
    page_count = 0

    try:
        with pdfplumber.open(file_path) as pdf:
            page_count = len(pdf.pages)
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)

        full_text = "\n\n".join(text_parts)
        return full_text, page_count
    except Exception as e:
        return f"[Error extracting text: {str(e)}]", 0


def _extract_text_fallback(file_path: str) -> Tuple[str, int]:
    """Fallback text extraction when pdfplumber is not available."""
    return "Contract text extraction requires pdfplumber. Please install requirements.", 1


def count_words(text: str) -> int:
    """Count words in text."""
    words = re.findall(r'\b\w+\b', text)
    return len(words)


def clean_text(text: str) -> str:
    """Clean and normalize contract text."""
    # Remove excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    # Remove page numbers
    text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
    return text.strip()


def get_file_size(file_path: str) -> int:
    """Get file size in bytes."""
    try:
        return os.path.getsize(file_path)
    except OSError:
        return 0
