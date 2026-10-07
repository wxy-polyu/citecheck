"""Index papers for the demo page and turn an agent result into JSON."""

from __future__ import annotations

import hashlib
import tempfile
from dataclasses import dataclass
from pathlib import Path

from citecheck.agent import SYSTEMS, AgentResult, answer_question
from citecheck.ingest import Chunk, parse_pdfs
from citecheck.llm import ROOT, from_env
from citecheck.retrieve import Retriever
from citecheck.sample_docs import write_examples


@dataclass
class Library:
    retriever: Retriever
    outline: list[dict]


_libraries: dict[str, Library] = {}


def outline_from_chunks(chunks: list[Chunk]) -> list[dict]:
    """Group chunks into papers and sections in the order they appear."""
    papers: list[dict] = []
    index: dict[str, dict] = {}
    for chunk in chunks:
        paper = index.get(chunk.paper_id)
        if paper is None:
            paper = {
                "id": chunk.paper_id,
                "title": chunk.paper_title,
                "pages": 0,
                "sections": [],
            }
            index[chunk.paper_id] = paper
            papers.append(paper)
        if chunk.page is not None:
            paper["pages"] = max(paper["pages"], chunk.page)
        sections: list[dict] = paper["sections"]
        if sections and sections[-1]["name"] == chunk.section:
            sections[-1]["chunks"] += 1
        else:
            sections.append({"name": chunk.section, "page": chunk.page, "chunks": 1})
    return papers


def result_payload(result: AgentResult) -> dict:
    spec = SYSTEMS[result.system]
    return {
        "answer": result.answer,
        "system": result.system,
        "verify": bool(spec["verify"]),
        "steps": result.steps,
        "latency_s": result.latency_s,
        "prompt_tokens": result.prompt_tokens,
        "completion_tokens": result.completion_tokens,
        "trace": result.trace,
        "claims": [
            {
                "text": claim.text,
                "label": claim.label,
                "verdict": claim.verdict,
                "section": claim.section,
                "page": claim.page,
                "paper_title": claim.paper_title,
                "evidence_index": _evidence_index(claim, result.evidence),
            }
            for claim in result.claims
        ],
        "evidence": [
            {
                "id": index,
                "paper_title": chunk.paper_title,
                "section": chunk.section,
                "page": chunk.page,
                "text": chunk.text,
            }
            for index, chunk in enumerate(result.evidence, start=1)
        ],
    }


def get_library(library_id: str) -> Library | None:
    return _libraries.get(library_id)


def index_sample(include_lite: bool) -> tuple[str, list[dict]]:
    library_id = "sample-lite" if include_lite else "sample"
    cached = _libraries.get(library_id)
    if cached is None:
        examples = ROOT / "examples"
        if not (examples / "widgetnet.pdf").exists():
            write_examples()
        paths = [examples / "widgetnet.pdf"]
        if include_lite:
            paths.append(examples / "widgetnet_lite.pdf")
        cached = _library_from_paths(paths)
        _libraries[library_id] = cached
    return library_id, cached.outline


def index_uploads(payloads: list[tuple[str, bytes]]) -> tuple[str, list[dict]]:
    digest = hashlib.sha256()
    for name, data in payloads:
        digest.update(name.encode())
        digest.update(b"\0")
        digest.update(data)
    library_id = digest.hexdigest()
    cached = _libraries.get(library_id)
    if cached is None:
        directory = Path(tempfile.mkdtemp(prefix="citecheck-"))
        paths: list[Path] = []
        used: set[str] = set()
        for name, data in payloads:
            safe_name = _unique_name(Path(name).name or "paper.pdf", used)
            path = directory / safe_name
            path.write_bytes(data)
            paths.append(path)
        cached = _library_from_paths(paths)
        _libraries[library_id] = cached
    return library_id, cached.outline


def ask(library_id: str, question: str, system: str) -> dict:
    library = _libraries[library_id]
    result = answer_question(
        question,
        library.retriever.chunks,
        from_env(),
        system=system,
        retriever=library.retriever,
    )
    return result_payload(result)


def _library_from_paths(paths: list[Path]) -> Library:
    chunks = parse_pdfs(paths)
    return Library(
        retriever=Retriever(chunks, mode="hybrid"),
        outline=outline_from_chunks(chunks),
    )


def _unique_name(name: str, used: set[str]) -> str:
    candidate = name
    stem = Path(name).stem or "paper"
    suffix = Path(name).suffix
    number = 2
    while candidate in used:
        candidate = f"{stem}-{number}{suffix}"
        number += 1
    used.add(candidate)
    return candidate


def _evidence_index(claim, evidence: list[Chunk]) -> int | None:
    if not claim.evidence_text:
        return None
    for index, chunk in enumerate(evidence, start=1):
        if (
            chunk.text == claim.evidence_text
            and chunk.section == claim.section
            and chunk.page == claim.page
            and chunk.paper_title == claim.paper_title
        ):
            return index
    return None
