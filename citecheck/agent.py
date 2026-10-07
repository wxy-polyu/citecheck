"""Query planning, draft answers, and claim verification."""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field

from citecheck.ingest import Chunk
from citecheck.llm import LLMClient
from citecheck.retrieve import Retriever

UNSUPPORTED_ANSWER = "The retrieved evidence does not support an answer to this question."
SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
EVIDENCE_ID = re.compile(r"\[E(\d+)\]", re.IGNORECASE)

SYSTEMS: dict[str, dict] = {
    "b1": {"retrieve": False, "plan": False, "verify": False, "mode": "hybrid"},
    "b2": {"retrieve": True, "plan": False, "verify": False, "mode": "hybrid"},
    "b3": {"retrieve": True, "plan": True, "verify": False, "mode": "hybrid"},
    "full": {"retrieve": True, "plan": True, "verify": True, "mode": "hybrid"},
    "no_planner": {"retrieve": True, "plan": False, "verify": True, "mode": "hybrid"},
    "embedding_only": {"retrieve": True, "plan": True, "verify": True, "mode": "embedding"},
    "no_verifier": {"retrieve": True, "plan": True, "verify": False, "mode": "hybrid"},
}


@dataclass
class VerifiedClaim:
    text: str
    label: str
    verdict: str
    section: str | None = None
    page: int | None = None
    paper_title: str | None = None
    evidence_text: str | None = None


@dataclass
class AgentResult:
    answer: str
    claims: list[VerifiedClaim] = field(default_factory=list)
    evidence: list[Chunk] = field(default_factory=list)
    steps: int = 0
    latency_s: float = 0.0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    system: str = "full"

    @property
    def success(self) -> bool:
        supported = [claim for claim in self.claims if claim.label == "supported"]
        return bool(supported) and all(claim.section for claim in supported)

    @property
    def unsupported_rate(self) -> float:
        if not self.claims:
            return 0.0
        uncertain = sum(claim.label != "supported" for claim in self.claims)
        return uncertain / len(self.claims)

    def citations(self) -> list[tuple[str, int | None]]:
        return [
            (claim.section or "", claim.page)
            for claim in self.claims
            if claim.label == "supported" and claim.section
        ]


def answer_question(
    question: str,
    chunks: list[Chunk],
    llm: LLMClient,
    *,
    system: str = "full",
    retriever: Retriever | None = None,
    top_k: int = 5,
) -> AgentResult:
    """Run one baseline or the full CiteCheck workflow."""
    if system not in SYSTEMS:
        raise ValueError(f"Unknown system: {system}")
    spec = SYSTEMS[system]
    if retriever is not None:
        chunks = retriever.chunks
    started = time.perf_counter()
    prompt_before = llm.usage.prompt_tokens
    completion_before = llm.usage.completion_tokens

    evidence: list[Chunk] = []
    steps = 0
    if spec["retrieve"]:
        if retriever is None:
            retriever = Retriever(chunks, mode=_index_mode(spec["mode"]))
        evidence, steps = collect_evidence(
            question,
            retriever,
            llm,
            plan=spec["plan"],
            mode=spec["mode"],
            top_k=top_k,
        )

    if not spec["retrieve"]:
        draft = _draft_without_paper(question, llm)
    elif not evidence:
        draft = "No relevant passage was retrieved."
    else:
        draft = _draft_with_evidence(question, evidence, llm)

    sentences = _sentences(draft)
    if spec["verify"]:
        claims = [_verify_sentence(sentence, evidence, llm) for sentence in sentences]
        supported = [claim for claim in claims if claim.label == "supported"]
        answer = " ".join(_render(claim) for claim in supported) if supported else UNSUPPORTED_ANSWER
    else:
        claims = [_claim_from_markers(sentence, evidence) for sentence in sentences]
        answer = draft.strip()

    return AgentResult(
        answer=answer,
        claims=claims,
        evidence=evidence,
        steps=steps,
        latency_s=time.perf_counter() - started,
        prompt_tokens=llm.usage.prompt_tokens - prompt_before,
        completion_tokens=llm.usage.completion_tokens - completion_before,
        system=system,
    )


def classify_claim(claim: str, passage: str, llm: LLMClient) -> str:
    """Label one claim against one passage. Used by the SciFact check."""
    chunk = Chunk(
        chunk_id="passage-0",
        paper_id="passage",
        paper_title="Passage",
        section="Abstract",
        page=None,
        paragraph=0,
        text=passage,
    )
    _verdict, _chunk = _judge(claim, [chunk], llm)
    return _verdict


def collect_evidence(
    question: str,
    retriever: Retriever,
    llm: LLMClient,
    *,
    plan: bool,
    mode: str,
    top_k: int,
) -> tuple[list[Chunk], int]:
    if not plan:
        return retriever.search(question, k=top_k, mode=mode), 1

    evidence: list[Chunk] = []
    steps = 0
    for round_index in range(2):
        decision = _plan(question, evidence[:8], llm)
        queries = [query for query in decision["queries"] if query.strip()][:3]
        if round_index > 0 and decision["action"] == "stop":
            break
        if not queries:
            queries = [question]
        for query in queries:
            evidence = _merge(evidence, retriever.search(query, k=top_k, mode=mode))
            steps += 1
        if decision["action"] == "stop":
            break
    return evidence[:8], steps


def _plan(question: str, evidence: list[Chunk], llm: LLMClient) -> dict:
    found = "No evidence yet."
    if evidence:
        found = "\n".join(
            f"[E{index}] {chunk.section}: {chunk.text[:400]}"
            for index, chunk in enumerate(evidence, start=1)
        )
    data = llm.complete_json(
        [
            {
                "role": "user",
                "content": (
                    "Task: plan retrieval\n"
                    "Decide the next lookup for a question about a research paper.\n"
                    "Return JSON with keys action and queries.\n"
                    'action is "search" or "stop". queries is a list of at most 3 search queries.\n'
                    "Use one query for a factual question. Split a question that connects "
                    "different sections, such as a method and an experiment.\n"
                    "Choose stop only when the evidence already answers the question.\n"
                    "Do not include retrieval scores.\n\n"
                    f"Question: {question}\n\nEvidence:\n{found}"
                ),
            }
        ]
    )
    action = str(data.get("action", "search")).lower()
    if action not in {"search", "stop"}:
        action = "search"
    raw_queries = data.get("queries") or []
    if isinstance(raw_queries, str):
        raw_queries = [raw_queries]
    queries = [str(query).strip() for query in raw_queries if str(query).strip()]
    return {"action": action, "queries": queries[:3]}


def _draft_without_paper(question: str, llm: LLMClient) -> str:
    return llm.complete(
        [
            {
                "role": "user",
                "content": (
                    "Task: draft answer\n"
                    "Answer the question in at most 3 short sentences. "
                    "You do not have the paper, so do not invent page citations.\n\n"
                    f"Question: {question}"
                ),
            }
        ]
    )


def _draft_with_evidence(question: str, evidence: list[Chunk], llm: LLMClient) -> str:
    return llm.complete(
        [
            {
                "role": "user",
                "content": (
                    "Task: draft answer\n"
                    "Answer only the question, in at most 3 short sentences, using only the passages.\n"
                    "Do not add other findings from the paper.\n"
                    "Put one fact in each sentence. Do not attach a yes or no to that fact.\n"
                    "End each sentence with its passage id before the period, for example: "
                    "The accuracy is 91 percent [E1].\n"
                    "If the passages do not answer the question, say that they do not.\n\n"
                    f"Question: {question}\n\n{_format_passages(evidence)}"
                ),
            }
        ]
    )


def _verify_sentence(sentence: str, evidence: list[Chunk], llm: LLMClient) -> VerifiedClaim:
    claim = _strip_markers(sentence)
    if not evidence:
        return VerifiedClaim(text=claim, label="uncertain", verdict="not_enough")
    verdict, chunk = _judge(claim, evidence, llm)
    if verdict != "supports" or chunk is None:
        return VerifiedClaim(
            text=claim,
            label="uncertain",
            verdict=verdict,
            section=chunk.section if chunk else None,
            page=chunk.page if chunk else None,
            paper_title=chunk.paper_title if chunk else None,
            evidence_text=chunk.text if chunk else None,
        )
    return VerifiedClaim(
        text=claim,
        label="supported",
        verdict="supports",
        section=chunk.section,
        page=chunk.page,
        paper_title=chunk.paper_title,
        evidence_text=chunk.text,
    )


def _judge(claim: str, passages: list[Chunk], llm: LLMClient) -> tuple[str, Chunk | None]:
    data = llm.complete_json(
        [
            {
                "role": "user",
                "content": (
                    "Task: verify claim\n"
                    "Decide whether the passages support or refute the claim.\n"
                    "Use only the passage text. Do not use a retrieval score.\n"
                    "Return JSON with keys label and evidence_id.\n"
                    'label is "supports", "refutes", or "not_enough".\n'
                    "evidence_id is the passage id such as E1, or null.\n"
                    "Choose supports only when that passage states the claim.\n"
                    "If the claim is about what the text does not say, choose not_enough.\n\n"
                    f"Claim: {claim}\n\n{_format_passages(passages)}"
                ),
            }
        ]
    )
    verdict = _normalize_verdict(str(data.get("label", "")))
    chunk = _chunk_from_id(data.get("evidence_id"), passages)
    if verdict == "supports" and chunk is None and len(passages) == 1:
        chunk = passages[0]
    if verdict == "supports" and chunk is None:
        return "not_enough", None
    return verdict, chunk


def _claim_from_markers(sentence: str, evidence: list[Chunk]) -> VerifiedClaim:
    claim = _strip_markers(sentence)
    ids = [int(value) for value in EVIDENCE_ID.findall(sentence)]
    chunk = None
    for number in ids:
        if 1 <= number <= len(evidence):
            chunk = evidence[number - 1]
            break
    if chunk is None:
        return VerifiedClaim(text=claim, label="uncertain", verdict="not_enough")
    return VerifiedClaim(
        text=claim,
        label="supported",
        verdict="supports",
        section=chunk.section,
        page=chunk.page,
        paper_title=chunk.paper_title,
        evidence_text=chunk.text,
    )


def _format_passages(chunks: list[Chunk]) -> str:
    blocks = []
    for index, chunk in enumerate(chunks, start=1):
        page = "unknown" if chunk.page is None else str(chunk.page)
        blocks.append(
            f"[E{index}] Paper: {chunk.paper_title} | Section: {chunk.section} | Page: {page}\n"
            f"{chunk.text}"
        )
    return "\n\n".join(blocks)


def _render(claim: VerifiedClaim) -> str:
    page = "unknown page" if claim.page is None else f"p. {claim.page}"
    paper = f"{claim.paper_title}, " if claim.paper_title else ""
    return f"{claim.text} ({paper}{claim.section}, {page})"


def _sentences(text: str) -> list[str]:
    parts = SENTENCE_SPLIT.split(text.strip())
    sentences: list[str] = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if sentences and re.fullmatch(r"(?:\[E\d+\]\s*)+", part, flags=re.IGNORECASE):
            sentences[-1] = f"{sentences[-1]} {part}"
            continue
        leading = re.match(r"^(?:\[E\d+\]\s*)+", part, flags=re.IGNORECASE)
        if sentences and leading and leading.end() < len(part):
            sentences[-1] = f"{sentences[-1]} {leading.group(0).strip()}"
            part = part[leading.end() :].strip()
        if part:
            sentences.append(part)
    return sentences


def _strip_markers(text: str) -> str:
    text = EVIDENCE_ID.sub("", text)
    text = re.sub(r"\s+([.!?])", r"\1", text)
    return re.sub(r"\s{2,}", " ", text).strip()


def _normalize_verdict(label: str) -> str:
    cleaned = label.strip().lower().replace("-", "_").replace(" ", "_")
    if cleaned in {"supports", "supported", "support"}:
        return "supports"
    if cleaned in {"refutes", "refute", "contradicts", "contradict"}:
        return "refutes"
    return "not_enough"


def _chunk_from_id(evidence_id: object, passages: list[Chunk]) -> Chunk | None:
    if evidence_id is None:
        return None
    match = re.search(r"(\d+)", str(evidence_id))
    if match is None:
        return None
    number = int(match.group(1))
    if 1 <= number <= len(passages):
        return passages[number - 1]
    return None


def _merge(existing: list[Chunk], new: list[Chunk]) -> list[Chunk]:
    seen = {chunk.chunk_id for chunk in existing}
    merged = list(existing)
    for chunk in new:
        if chunk.chunk_id not in seen:
            merged.append(chunk)
            seen.add(chunk.chunk_id)
    return merged


def _index_mode(mode: str) -> str:
    return "hybrid" if mode == "hybrid" else mode
