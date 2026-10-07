"""Outline grouping and demo API errors."""

import unittest

from fastapi.testclient import TestClient

from citecheck.ingest import Chunk
from citecheck.web.app import app
from citecheck.web.service import outline_from_chunks


def _chunk(paper_id: str, title: str, section: str, page: int, text: str) -> Chunk:
    return Chunk(f"{paper_id}-{section}-{page}", paper_id, title, section, page, 0, text)


class OutlineTest(unittest.TestCase):
    def test_sections_stay_in_reading_order(self) -> None:
        chunks = [
            _chunk("a", "WidgetNet", "1 Introduction", 2, "intro"),
            _chunk("a", "WidgetNet", "1 Introduction", 2, "more"),
            _chunk("a", "WidgetNet", "3 Experiments", 5, "result"),
            _chunk("b", "WidgetNet-Lite", "Abstract", 1, "lite"),
        ]
        outline = outline_from_chunks(chunks)
        self.assertEqual([paper["title"] for paper in outline], ["WidgetNet", "WidgetNet-Lite"])
        self.assertEqual(outline[0]["pages"], 5)
        self.assertEqual(
            outline[0]["sections"],
            [
                {"name": "1 Introduction", "page": 2, "chunks": 2},
                {"name": "3 Experiments", "page": 5, "chunks": 1},
            ],
        )


class DemoApiTest(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_ask_without_an_index_is_rejected(self) -> None:
        response = self.client.post(
            "/api/ask",
            json={"library_id": "missing", "question": "What accuracy?", "system": "full"},
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"]["code"], "unknown_library")

    def test_empty_question_is_rejected(self) -> None:
        response = self.client.post(
            "/api/ask",
            json={"library_id": "missing", "question": "  ", "system": "full"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"]["code"], "empty_question")

    def test_upload_without_a_pdf_is_rejected(self) -> None:
        response = self.client.post("/api/library", data={"source": "upload", "include_lite": "false"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"]["code"], "need_pdf")

    def test_page_is_served(self) -> None:
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("CiteCheck", response.text)
        self.assertIn('id="library-sidebar"', response.text)
        self.assertIn('id="detail-panel"', response.text)
        self.assertIn('id="history-drawer"', response.text)
        self.assertIn('id="question"', response.text)
