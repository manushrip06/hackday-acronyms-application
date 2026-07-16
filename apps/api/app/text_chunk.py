from __future__ import annotations

DEFAULT_MAX_CHARS = 6000


def chunk_text(text: str, *, max_chars: int = DEFAULT_MAX_CHARS) -> list[str]:
    """Split text into NLP-sized chunks, breaking on whitespace when possible."""
    text = (text or "").strip()
    if not text:
        return []
    if len(text) <= max_chars:
        return [text]

    chunks: list[str] = []
    start = 0
    length = len(text)

    while start < length:
        end = min(start + max_chars, length)

        if end < length and not text[end].isspace():
            while end < length and not text[end].isspace():
                end += 1

        piece = text[start:end].strip()
        if piece:
            chunks.append(piece)

        start = end
        while start < length and text[start].isspace():
            start += 1

    return chunks
