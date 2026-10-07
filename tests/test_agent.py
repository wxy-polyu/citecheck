"""Agent workflow with a fake model, so the test does not call an API."""

import unittest

from citecheck.agent import answer_question
from citecheck.ingest import Chunk
from citecheck.llm import TokenUsage


class FakeRetriever:
    def __init__(self, chunks: list[Chunk]) -> None:
        self.chunks = chunks
        self.calls: list[str] = []

    def search(self, query: str, k: int = 5, mode: str | None = None) -> list[Chunk]:
        del k, mode
        self.calls.append(query)
        return self.chunks[:1]


class FakeLLM:
    def __init__(self) -> None:
        self.usage = TokenUsage()
        self.plans = 0

    def complete(self, messages, **kwargs):
        del messages, kwargs
        self.usage.add(5, 7)
        return "WidgetNet reaches 91 percent accuracy. [E1]"

    def complete_json(self, messages, **kwargs):
        del kwargs
        self.usage.add(3, 2)
        text = messages[-1]["content"]
        if "Task: plan retrieval" in text:
            self.plans += 1
            if self.plans == 1:
                return {"action": "search", "queries": ["WidgetNet accuracy"]}
            return {"action": "stop", "queries": []}
        if "Task: verify claim" in text:
            return {"label": "supports", "evidence_id": "E1"}
        raise AssertionError(text[:120])


class AgentTest(unittest.TestCase):
    def setUp(self) -> None:
        self.chunk = Chunk(
            "c1",
            "widgetnet",
            "WidgetNet",
            "3 Experiments",
            5,
            0,
            "On Widget-100, WidgetNet reaches 91 percent accuracy.",
        )

    def test_full_system_checks_the_claim_and_keeps_the_citation(self) -> None:
        retriever = FakeRetriever([self.chunk])
        result = answer_question(
            "What accuracy does WidgetNet reach?",
            [self.chunk],
            FakeLLM(),
            system="full",
            retriever=retriever,
        )
        self.assertEqual(result.steps, 1)
        self.assertEqual(retriever.calls, ["WidgetNet accuracy"])
        self.assertEqual(result.claims[0].label, "supported")
        self.assertEqual(result.claims[0].page, 5)
        self.assertIn("3 Experiments", result.answer)
        self.assertEqual(
            result.trace,
            [
                {"action": "search", "queries": ["WidgetNet accuracy"]},
                {"action": "stop", "queries": []},
            ],
        )
        self.assertTrue(result.success)
        self.assertEqual(result.unsupported_rate, 0.0)

    def test_prompt_only_has_no_citation(self) -> None:
        result = answer_question("What accuracy does WidgetNet reach?", [], FakeLLM(), system="b1")
        self.assertEqual(result.steps, 0)
        self.assertEqual(result.trace, [{"action": "none", "queries": []}])
        self.assertFalse(result.success)
        self.assertEqual(result.unsupported_rate, 1.0)

    def test_single_pass_does_not_plan_or_verify(self) -> None:
        llm = FakeLLM()
        retriever = FakeRetriever([self.chunk])
        result = answer_question(
            "What accuracy does WidgetNet reach?",
            [self.chunk],
            llm,
            system="b2",
            retriever=retriever,
        )
        self.assertEqual(llm.plans, 0)
        self.assertEqual(
            result.trace,
            [{"action": "single", "queries": ["What accuracy does WidgetNet reach?"]}],
        )
        self.assertEqual(retriever.calls, ["What accuracy does WidgetNet reach?"])
        self.assertEqual(result.claims[0].section, "3 Experiments")


if __name__ == "__main__":
    unittest.main()
