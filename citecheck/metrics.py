"""Answer, evidence, and citation metrics used by the evaluation script."""

from __future__ import annotations

import re
from collections import Counter

TOKEN = re.compile(r"[a-z0-9]+")
SECTION_NUMBER = re.compile(r"^\d+(?:\.\d+)*\s+")


def tokens(text: str) -> list[str]:
    return TOKEN.findall(text.lower())


def token_f1(prediction: str, golds: list[str]) -> float:
    """Highest token F1 against any gold answer."""
    if not golds:
        return 0.0
    return max(_f1(prediction, gold) for gold in golds)


def evidence_recall(retrieved: list[str], gold: list[str]) -> float | None:
    """Fraction of gold passages that appear in the retrieved chunks.

    Returns None when the question has no gold evidence, so the average can skip it.
    """
    if not gold:
        return None
    hits = 0
    for passage in gold:
        if any(_passage_match(passage, candidate) for candidate in retrieved):
            hits += 1
    return hits / len(gold)


def citation_scores(
    predicted: list[tuple[str, int | None]],
    gold: list[tuple[str, int | None]],
) -> tuple[float, float] | None:
    """Precision and recall. A citation matches only when section and page both match.

    Returns None when the dataset has no page-level gold citations.
    """
    if not any(page is not None for _section, page in gold):
        return None
    predicted_set = {_cite_key(section, page) for section, page in predicted}
    gold_set = {_cite_key(section, page) for section, page in gold}
    predicted_set.discard(None)
    gold_set.discard(None)
    if not gold_set:
        return None
    if not predicted_set:
        return 0.0, 0.0
    matched = predicted_set & gold_set
    return len(matched) / len(predicted_set), len(matched) / len(gold_set)


def unsupported_rate(labels: list[str]) -> float:
    if not labels:
        return 0.0
    uncertain = sum(label != "supported" for label in labels)
    return uncertain / len(labels)


def _f1(prediction: str, gold: str) -> float:
    pred_tokens = tokens(prediction)
    gold_tokens = tokens(gold)
    if not pred_tokens or not gold_tokens:
        return 0.0
    overlap = sum((Counter(pred_tokens) & Counter(gold_tokens)).values())
    if overlap == 0:
        return 0.0
    precision = overlap / len(pred_tokens)
    recall = overlap / len(gold_tokens)
    return 2 * precision * recall / (precision + recall)


def _passage_match(gold: str, retrieved: str) -> bool:
    gold_text = " ".join(tokens(gold))
    retrieved_text = " ".join(tokens(retrieved))
    if len(gold_text) >= 20 and gold_text in retrieved_text:
        return True
    return _f1(retrieved, gold) >= 0.5


def _cite_key(section: str, page: int | None) -> tuple[str, int] | None:
    if page is None:
        return None
    normalized = SECTION_NUMBER.sub("", section.strip().lower())
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized, int(page)
