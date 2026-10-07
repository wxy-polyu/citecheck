"""Parser and chunking tests, using the synthetic sample papers."""

import tempfile
import unittest
from pathlib import Path

from citecheck.ingest import Paragraph, chunks_from_paragraphs, parse_pdf
from citecheck.sample_docs import WIDGETNET, write_pdf


class IngestTest(unittest.TestCase):
    def test_sample_pdf_keeps_section_and_page(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "widgetnet.pdf"
            write_pdf(path, WIDGETNET)
            chunks = parse_pdf(path)

        by_section = {chunk.section: chunk for chunk in chunks}
        self.assertEqual(by_section["Abstract"].page, 1)
        self.assertIn("counts widgets", by_section["Abstract"].text)
        self.assertEqual(by_section["1 Introduction"].page, 2)
        self.assertEqual(by_section["2 Method"].page, 3)
        self.assertEqual(by_section["2.1 Training"].page, 4)
        self.assertEqual(by_section["3 Experiments"].page, 5)
        self.assertIn("91 percent", by_section["3 Experiments"].text)
        self.assertEqual(by_section["4 Conclusion"].page, 6)
        self.assertEqual(chunks[0].paper_title, "WidgetNet: A Sample Paper for Citation Checking")

    def test_chunks_do_not_cross_sections(self) -> None:
        paragraphs = [
            Paragraph("Method", 1, "A" * 800),
            Paragraph("Method", 1, "B" * 800),
            Paragraph("Results", 2, "C" * 100),
        ]
        chunks = chunks_from_paragraphs("paper", "Title", paragraphs, max_chars=1200)
        self.assertTrue(all("A" not in chunk.text or "C" not in chunk.text for chunk in chunks))
        self.assertTrue(any(chunk.section == "Results" and chunk.page == 2 for chunk in chunks))
        self.assertGreater(len(chunks), 2)


class ParseJsonTest(unittest.TestCase):
    def test_parse_json_accepts_a_fence(self) -> None:
        from citecheck.llm import parse_json

        self.assertEqual(parse_json('```json\n{"action": "stop"}\n```'), {"action": "stop"})


if __name__ == "__main__":
    unittest.main()
