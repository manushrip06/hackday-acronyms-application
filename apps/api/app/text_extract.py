from __future__ import annotations

from io import BytesIO
from pathlib import Path


def extract_text(filename: str, raw: bytes) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix in {".md", ".txt", ".text", ".csv"}:
        return raw.decode("utf-8", errors="replace")
    if suffix == ".pdf":
        return _extract_pdf(raw)
    # Fallback: try utf-8
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"Unsupported file type: {suffix or '(none)'}") from exc


def _extract_pdf(raw: bytes) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise ValueError("PDF support unavailable; paste text or upload .md/.txt") from exc
    reader = PdfReader(BytesIO(raw))
    parts: list[str] = []
    for page in reader.pages:
        parts.append(page.extract_text() or "")
    text = "\n".join(parts).strip()
    if not text:
        raise ValueError("Could not extract text from PDF; paste text instead")
    return text
