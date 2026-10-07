"""Parse a paper PDF into section-aware chunks with page numbers."""

from __future__ import annotations

import re
import statistics
from dataclasses import dataclass
from pathlib import Path

NUMBERED_HEADING = re.compile(r"^\d+(?:\.\d+)*\s+\S")
KEYWORD_HEADINGS = {
    "abstract",
    "references",
    "acknowledgements",
    "acknowledgments",
    "appendix",
}
MAX_CHARS = 1200


@dataclass
class Paragraph:
    section: str
    page: int | None
    text: str


@dataclass
class Chunk:
    chunk_id: str
    paper_id: str
    paper_title: str
    section: str
    page: int | None
    paragraph: int
    text: str


@dataclass
class _Line:
    text: str
    page: int
    size: float


def parse_pdf(path: str | Path) -> list[Chunk]:
    """Extract chunks from one PDF, keeping section titles and page numbers."""
    path = Path(path)
    lines = _extract_lines(path)
    paragraphs, title = _paragraphs_from_lines(lines)
    return chunks_from_paragraphs(path.stem, title or path.stem, paragraphs)


def parse_pdfs(paths: list[str | Path]) -> list[Chunk]:
    chunks: list[Chunk] = []
    for path in paths:
        chunks.extend(parse_pdf(path))
    return chunks


def chunks_from_paragraphs(
    paper_id: str,
    paper_title: str,
    paragraphs: list[Paragraph],
    *,
    max_chars: int = MAX_CHARS,
) -> list[Chunk]:
    """Pack same-section paragraphs into chunks of about 800–1200 characters."""
    chunks: list[Chunk] = []
    buffer = ""
    buffer_section = ""
    buffer_page: int | None = None

    def emit() -> None:
        nonlocal buffer
        text = buffer.strip()
        if not text:
            buffer = ""
            return
        chunks.append(
            Chunk(
                chunk_id=f"{paper_id}-{len(chunks)}",
                paper_id=paper_id,
                paper_title=paper_title,
                section=buffer_section or "Body",
                page=buffer_page,
                paragraph=len(chunks),
                text=text,
            )
        )
        buffer = ""

    for paragraph in paragraphs:
        pieces = _split_long(paragraph.text, max_chars)
        for piece in pieces:
            same_section = paragraph.section == buffer_section
            if buffer and (not same_section or len(buffer) + 1 + len(piece) > max_chars):
                emit()
            if not buffer:
                buffer_section = paragraph.section
                buffer_page = paragraph.page
            buffer = f"{buffer} {piece}".strip()
    emit()
    return chunks


def _extract_lines(path: Path) -> list[_Line]:
    import pymupdf

    document = pymupdf.open(path)
    lines: list[_Line] = []
    try:
        for page_index, page in enumerate(document, start=1):
            for block in page.get_text("dict").get("blocks", []):
                if block.get("type") != 0:
                    continue
                for line in block.get("lines", []):
                    spans = line.get("spans", [])
                    text = "".join(span.get("text", "") for span in spans).strip()
                    if not text or re.fullmatch(r"\d{1,3}", text):
                        continue
                    size = max((float(span.get("size", 0)) for span in spans), default=0)
                    lines.append(_Line(text=text, page=page_index, size=size))
    finally:
        document.close()
    return lines


def _paragraphs_from_lines(lines: list[_Line]) -> tuple[list[Paragraph], str]:
    body_sizes = [
        line.size
        for line in lines
        if len(line.text) > 40 and not NUMBERED_HEADING.match(line.text)
    ]
    body_size = statistics.median(body_sizes or [line.size for line in lines] or [12])
    title = ""
    section = "Front matter"
    paragraphs: list[Paragraph] = []
    buffer: list[str] = []
    buffer_page: int | None = None

    def flush() -> None:
        nonlocal buffer
        text = " ".join(buffer).strip()
        if text:
            paragraphs.append(Paragraph(section=section, page=buffer_page, text=text))
        buffer = []

    for line in lines:
        if _is_title(line, body_size, title):
            flush()
            title = line.text
            continue
        if _is_heading(line, body_size):
            flush()
            section = line.text
            continue
        if not buffer:
            buffer_page = line.page
        buffer.append(line.text)
    flush()
    return paragraphs, title


def _is_title(line: _Line, body_size: float, title: str) -> bool:
    return (
        not title
        and line.page == 1
        and line.size >= body_size + 5
        and not NUMBERED_HEADING.match(line.text)
        and len(line.text) <= 140
    )


def _is_heading(line: _Line, body_size: float) -> bool:
    if NUMBERED_HEADING.match(line.text) and len(line.text) <= 120:
        return True
    if line.text.lower() in KEYWORD_HEADINGS:
        return True
    return line.size >= body_size + 2 and len(line.text) <= 80


def _split_long(text: str, max_chars: int) -> list[str]:
    text = text.strip()
    if len(text) <= max_chars:
        return [text] if text else []
    sentences = re.split(r"(?<=[.!?])\s+", text)
    pieces: list[str] = []
    current = ""
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        if len(sentence) > max_chars:
            if current:
                pieces.append(current)
                current = ""
            for start in range(0, len(sentence), max_chars):
                pieces.append(sentence[start : start + max_chars])
            continue
        if current and len(current) + 1 + len(sentence) > max_chars:
            pieces.append(current)
            current = sentence
        else:
            current = f"{current} {sentence}".strip()
    if current:
        pieces.append(current)
    return pieces
