"""Run B1, B2, B3, CiteCheck, and the ablations, then write the metrics."""

from __future__ import annotations

import argparse
import json
import tarfile
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

from citecheck.agent import SYSTEMS, AgentResult, answer_question, classify_claim
from citecheck.ingest import Chunk, chunks_from_paragraphs, parse_pdfs
from citecheck.ingest import Paragraph
from citecheck.llm import ROOT, from_env
from citecheck.metrics import citation_scores, evidence_recall, token_f1
from citecheck.retrieve import Retriever

DEFAULT_LIMITS = {"custom": None, "qasper": 20, "scifact": 50}
QASPER_URL = "https://qasper-dataset.s3.us-west-2.amazonaws.com/qasper-train-dev-v0.3.tgz"
SCIFACT_URL = "https://scifact.s3-us-west-2.amazonaws.com/release/latest/data.tar.gz"


@dataclass
class QuestionItem:
    id: str
    question: str
    answers: list[str]
    evidence: list[str]
    citations: list[tuple[str, int | None]]
    pdfs: list[Path] = field(default_factory=list)
    chunks: list[Chunk] = field(default_factory=list)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Evaluate CiteCheck and the baselines.")
    parser.add_argument("--dataset", choices=["custom", "qasper", "scifact"], default="custom")
    parser.add_argument("--questions", type=Path, default=ROOT / "examples" / "custom_questions.json")
    parser.add_argument("--systems", default="b1,b2,b3,full")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--output", type=Path, default=ROOT / "data" / "results" / "latest.json")
    args = parser.parse_args(argv)

    limit = DEFAULT_LIMITS[args.dataset] if args.limit is None else args.limit
    llm = from_env()
    if args.dataset == "scifact":
        summary = _run_scifact(llm, limit, args.output)
    else:
        systems = _parse_systems(args.systems)
        if args.dataset == "custom":
            if not args.questions.exists():
                from citecheck.sample_docs import write_examples

                write_examples()
            questions = load_custom_questions(args.questions, ROOT)
        else:
            questions = load_qasper(limit)
            limit = None
        if limit is not None:
            questions = questions[:limit]
        summary = _run_questions(questions, systems, llm, args.output)
    print(json.dumps(summary, indent=2))


def load_custom_questions(path: Path, base: Path) -> list[QuestionItem]:
    records = json.loads(path.read_text(encoding="utf-8"))
    questions = []
    for record in records:
        questions.append(
            QuestionItem(
                id=str(record["id"]),
                question=record["question"],
                answers=list(record.get("answers") or []),
                evidence=list(record.get("evidence") or []),
                citations=[
                    (item["section"], item.get("page")) for item in record.get("citations") or []
                ],
                pdfs=[base / pdf for pdf in record.get("pdfs") or []],
            )
        )
    return questions


def load_qasper(limit: int | None) -> list[QuestionItem]:
    """Load a QASPER dev slice. Evidence is paragraphs, so page citations are not scored."""
    questions: list[QuestionItem] = []
    for paper_id, paper in _read_qasper_dev().items():
        if limit is not None and len(questions) >= limit:
            break
        paper = dict(paper)
        paper["id"] = paper_id
        chunks = _qasper_chunks(paper)
        flat = [chunk.text for chunk in chunks]
        for qa in paper.get("qas") or []:
            if limit is not None and len(questions) >= limit:
                break
            question = (qa.get("question") or "").strip()
            gold = _qasper_gold(qa.get("answers") or [], flat)
            if not question or gold is None:
                continue
            answer_texts, evidence = gold
            questions.append(
                QuestionItem(
                    id=str(qa.get("question_id") or f"{paper_id}-{len(questions)}"),
                    question=question,
                    answers=answer_texts,
                    evidence=evidence,
                    citations=[],
                    chunks=chunks,
                )
            )
    return questions


def _run_questions(
    questions: list[QuestionItem],
    systems: list[str],
    llm: object,
    output: Path,
) -> dict:
    modes = {SYSTEMS[system]["mode"] for system in systems if SYSTEMS[system]["retrieve"]}
    index_mode = "hybrid" if "hybrid" in modes or {"bm25", "embedding"} <= modes else (modes.pop() if modes else "bm25")
    retrievers: dict[tuple, Retriever] = {}
    rows = []
    for item in questions:
        retriever = _retriever_for(item, index_mode, retrievers)
        chunks = retriever.chunks if retriever is not None else item.chunks
        for system in systems:
            try:
                result = answer_question(
                    item.question,
                    chunks,
                    llm,
                    system=system,
                    retriever=retriever if SYSTEMS[system]["retrieve"] else None,
                )
                rows.append(_row(item, result))
            except Exception as exc:
                rows.append({"id": item.id, "system": system, "error": str(exc)})
            print(f"{item.id} {system} done", flush=True)
    summary = _summarize(rows)
    _write(output, {"summary": summary, "rows": rows})
    return summary


def _run_scifact(llm: object, limit: int | None, output: Path) -> dict:
    claims = _load_scifact(limit)
    rows = []
    correct = 0
    for claim in claims:
        try:
            prompt_before = llm.usage.prompt_tokens
            completion_before = llm.usage.completion_tokens
            predicted = classify_claim(claim["claim"], claim["abstract"], llm)
            hit = predicted == claim["label"]
            correct += int(hit)
            rows.append(
                {
                    "id": claim["id"],
                    "gold": claim["label"],
                    "predicted": predicted,
                    "correct": hit,
                    "prompt_tokens": llm.usage.prompt_tokens - prompt_before,
                    "completion_tokens": llm.usage.completion_tokens - completion_before,
                }
            )
        except Exception as exc:
            rows.append({"id": claim["id"], "error": str(exc)})
        print(f"{claim['id']} scifact done", flush=True)
    scored = [row for row in rows if "correct" in row]
    summary = {
        "dataset": "scifact",
        "n": len(scored),
        "label_accuracy": correct / len(scored) if scored else 0.0,
        "prompt_tokens": llm.usage.prompt_tokens,
        "completion_tokens": llm.usage.completion_tokens,
    }
    _write(output, {"summary": summary, "rows": rows})
    return summary


def _load_scifact(limit: int | None) -> list[dict]:
    """Load labeled SciFact dev claims with the cited abstract."""
    directory = _extract_archive(
        _download(SCIFACT_URL, ROOT / "data" / "scifact" / "data.tar.gz"),
        ROOT / "data" / "scifact" / "extracted",
    )
    abstracts = {}
    with (directory / "data" / "corpus.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            paper = json.loads(line)
            abstract = paper.get("abstract") or ""
            if isinstance(abstract, list):
                abstract = " ".join(abstract)
            abstracts[str(paper.get("doc_id"))] = abstract
    selected = []
    with (directory / "data" / "claims_dev.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            claim = json.loads(line)
            for doc_id, rationales in (claim.get("evidence") or {}).items():
                labels = {str(item.get("label") or "").upper() for item in rationales}
                if labels == {"SUPPORT"}:
                    verdict = "supports"
                elif labels == {"CONTRADICT"}:
                    verdict = "refutes"
                else:
                    continue
                abstract = abstracts.get(str(doc_id), "")
                if not abstract:
                    continue
                selected.append(
                    {
                        "id": f"{claim.get('id')}-{doc_id}",
                        "claim": claim["claim"],
                        "abstract": abstract,
                        "label": verdict,
                    }
                )
                if limit is not None and len(selected) >= limit:
                    return selected
    return selected


def _retriever_for(
    item: QuestionItem,
    mode: str,
    cache: dict[tuple, Retriever],
) -> Retriever | None:
    if item.chunks:
        key = (item.chunks[0].paper_id, mode)
    else:
        key = (tuple(str(path) for path in item.pdfs), mode)
    if key not in cache:
        chunks = item.chunks or parse_pdfs(item.pdfs)
        cache[key] = Retriever(chunks, mode=mode)
    return cache[key]


def _row(item: QuestionItem, result: AgentResult) -> dict:
    retrieved = [chunk.text for chunk in result.evidence]
    citation = citation_scores(result.citations(), item.citations)
    row = {
        "id": item.id,
        "system": result.system,
        "prediction": result.answer,
        "token_f1": token_f1(result.answer, item.answers),
        "evidence_recall": evidence_recall(retrieved, item.evidence),
        "unsupported_rate": result.unsupported_rate,
        "success": result.success,
        "steps": result.steps,
        "latency_s": round(result.latency_s, 3),
        "prompt_tokens": result.prompt_tokens,
        "completion_tokens": result.completion_tokens,
    }
    if citation is not None:
        row["citation_precision"], row["citation_recall"] = citation
    return row


def _summarize(rows: list[dict]) -> dict:
    by_system: dict[str, list[dict]] = {}
    for row in rows:
        if "error" in row:
            continue
        by_system.setdefault(row["system"], []).append(row)
    summary = {}
    for system, group in by_system.items():
        summary[system] = {
            "n": len(group),
            "token_f1": _mean(group, "token_f1"),
            "evidence_recall": _mean(group, "evidence_recall"),
            "citation_precision": _mean(group, "citation_precision"),
            "citation_recall": _mean(group, "citation_recall"),
            "unsupported_rate": _mean(group, "unsupported_rate"),
            "success_rate": _mean_bool(group, "success"),
            "steps": _mean(group, "steps"),
            "latency_s": _mean(group, "latency_s"),
            "prompt_tokens": sum(row["prompt_tokens"] for row in group),
            "completion_tokens": sum(row["completion_tokens"] for row in group),
        }
    return summary


def _qasper_chunks(paper: dict) -> list[Chunk]:
    paragraphs = []
    abstract = (paper.get("abstract") or "").strip()
    if abstract:
        paragraphs.append(Paragraph(section="Abstract", page=None, text=abstract))
    for section, text in _qasper_paragraphs(paper.get("full_text")):
        paragraphs.append(Paragraph(section=section, page=None, text=text))
    return chunks_from_paragraphs(str(paper.get("id")), paper.get("title") or "Paper", paragraphs)


def _qasper_paragraphs(full_text: object) -> list[tuple[str, str]]:
    paragraphs = []
    if isinstance(full_text, list):
        sections = full_text
    elif isinstance(full_text, dict):
        sections = [
            {"section_name": name, "paragraphs": texts}
            for name, texts in zip(full_text.get("section_name") or [], full_text.get("paragraphs") or [])
        ]
    else:
        sections = []
    for section in sections:
        name = section.get("section_name") or "Body"
        for text in section.get("paragraphs") or []:
            if text and str(text).strip():
                paragraphs.append((name, str(text).strip()))
    return paragraphs


def _read_qasper_dev() -> dict:
    archive = _download(QASPER_URL, ROOT / "data" / "qasper" / "qasper-train-dev-v0.3.tgz")
    json_path = ROOT / "data" / "qasper" / "qasper-dev-v0.3.json"
    if not json_path.exists():
        with tarfile.open(archive, "r:gz") as bundle:
            member = next(item for item in bundle.getmembers() if item.name.endswith("qasper-dev-v0.3.json"))
            extracted = bundle.extractfile(member)
            if extracted is None:
                raise RuntimeError("QASPER dev file was missing from the archive.")
            json_path.write_bytes(extracted.read())
    return json.loads(json_path.read_text(encoding="utf-8"))


def _download(url: str, path: Path) -> Path:
    if path.exists() and path.stat().st_size > 0:
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {url}", flush=True)
    urllib.request.urlretrieve(url, path)
    return path


def _extract_archive(archive: Path, directory: Path) -> Path:
    marker = directory / "data" / "corpus.jsonl"
    if marker.exists():
        return directory
    directory.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive, "r:gz") as bundle:
        bundle.extractall(directory, filter="data")
    return directory


def _qasper_gold(answer_group: object, paragraphs: list[str]) -> tuple[list[str], list[str]] | None:
    annotators = _annotators(answer_group)
    answers: list[str] = []
    evidence: list[str] = []
    for annotator in annotators:
        for answer in _answer_records(annotator):
            if answer.get("unanswerable"):
                continue
            free_form = (answer.get("free_form_answer") or "").strip()
            spans = [span for span in answer.get("extractive_spans") or [] if span]
            if free_form:
                answers.append(free_form)
            if spans:
                answers.append(" ".join(spans))
            if answer.get("yes_no") is True:
                answers.append("yes")
            elif answer.get("yes_no") is False:
                answers.append("no")
            evidence.extend(_evidence_texts(answer, paragraphs))
    if not answers:
        return None
    return answers, _unique(evidence)


def _annotators(answer_group: object) -> list[dict]:
    if isinstance(answer_group, dict):
        if "answer" in answer_group:
            return [answer_group]
        return []
    return [item for item in answer_group or [] if isinstance(item, dict)]


def _answer_records(annotator: dict) -> list[dict]:
    answer_value = annotator.get("answer")
    if isinstance(answer_value, dict):
        return [answer_value]
    if isinstance(answer_value, list):
        return [item for item in answer_value if isinstance(item, dict)]
    if any(key in annotator for key in ("unanswerable", "extractive_spans", "free_form_answer")):
        return [annotator]
    return []


def _evidence_texts(answer: dict, paragraphs: list[str]) -> list[str]:
    evidence = _clean_evidence(answer.get("evidence"), paragraphs)
    if evidence:
        return evidence
    return _clean_evidence(answer.get("highlighted_evidence"), paragraphs)


def _clean_evidence(values: object, paragraphs: list[str]) -> list[str]:
    texts = []
    for value in values or []:
        if value is None:
            continue
        text = str(value).strip()
        if text.isdigit() and int(text) < len(paragraphs):
            texts.append(paragraphs[int(text)])
        elif len(text) > 20:
            texts.append(text)
    return texts


def _unique(values: list[str]) -> list[str]:
    seen = set()
    ordered = []
    for value in values:
        if value not in seen:
            seen.add(value)
            ordered.append(value)
    return ordered


def _parse_systems(text: str) -> list[str]:
    systems = [item.strip() for item in text.split(",") if item.strip()]
    unknown = [item for item in systems if item not in SYSTEMS]
    if unknown:
        raise ValueError(f"Unknown systems: {', '.join(unknown)}")
    return systems


def _mean(rows: list[dict], key: str) -> float | None:
    values = [row[key] for row in rows if row.get(key) is not None]
    if not values:
        return None
    return sum(values) / len(values)


def _mean_bool(rows: list[dict], key: str) -> float:
    if not rows:
        return 0.0
    return sum(bool(row.get(key)) for row in rows) / len(rows)


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
