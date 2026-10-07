"""Metric definitions from the proposal, plus the public dataset record shape."""

import unittest

from citecheck.evaluate import _qasper_chunks, _qasper_gold
from citecheck.metrics import citation_scores, evidence_recall, token_f1, unsupported_rate


class MetricsTest(unittest.TestCase):
    def test_token_f1_uses_the_best_gold_answer(self) -> None:
        score = token_f1("WidgetNet reaches 91 percent accuracy.", ["80 percent", "91 percent"])
        self.assertGreater(score, 0.4)

    def test_citation_requires_section_and_page(self) -> None:
        precision, recall = citation_scores(
            [("3 Experiments", 5), ("2 Method", 3)],
            [("Experiments", 5)],
        )
        self.assertEqual(precision, 0.5)
        self.assertEqual(recall, 1.0)
        self.assertIsNone(citation_scores([("Experiments", 5)], [("Experiments", None)]))

    def test_evidence_recall_matches_a_contained_passage(self) -> None:
        gold = "On Widget-100, WidgetNet reaches 91 percent accuracy."
        retrieved = ["Intro text. " + gold]
        self.assertEqual(evidence_recall(retrieved, [gold]), 1.0)
        self.assertIsNone(evidence_recall(retrieved, []))

    def test_unsupported_rate(self) -> None:
        self.assertEqual(unsupported_rate(["supported", "uncertain"]), 0.5)


class QasperRecordTest(unittest.TestCase):
    def test_raw_qasper_record_keeps_section_text_and_gold_evidence(self) -> None:
        paper = {
            "id": "p1",
            "title": "Widgets",
            "abstract": "This paper studies widgets.",
            "full_text": [
                {"section_name": "Introduction", "paragraphs": ["The model uses widgets in every experiment."]}
            ],
        }
        chunks = _qasper_chunks(paper)
        self.assertIn("Introduction", [chunk.section for chunk in chunks])
        self.assertIsNone(chunks[0].page)
        gold = _qasper_gold(
            [
                {
                    "answer": {
                        "unanswerable": False,
                        "extractive_spans": ["widgets"],
                        "yes_no": None,
                        "free_form_answer": "",
                        "evidence": ["The model uses widgets in every experiment."],
                        "highlighted_evidence": [],
                    }
                }
            ],
            [chunk.text for chunk in chunks],
        )
        self.assertIsNotNone(gold)
        answers, evidence = gold
        self.assertIn("widgets", answers)
        self.assertEqual(evidence, ["The model uses widgets in every experiment."])


if __name__ == "__main__":
    unittest.main()
