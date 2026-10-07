"""Checks the language-model client without calling a real API."""

import unittest
from types import SimpleNamespace

from citecheck.llm import LLMClient, from_env


class FakeCompletions:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content='{"ok": true}'))],
            usage=SimpleNamespace(prompt_tokens=11, completion_tokens=4),
        )


class FakeClient:
    def __init__(self) -> None:
        self.chat = SimpleNamespace(completions=FakeCompletions())


class LLMClientTest(unittest.TestCase):
    def test_complete_records_tokens_and_json_mode(self) -> None:
        fake = FakeClient()
        client = LLMClient(model="test-model", client=fake)

        text = client.complete(
            [{"role": "user", "content": "hello"}],
            json_mode=True,
        )

        self.assertEqual(text, '{"ok": true}')
        self.assertEqual(client.usage.prompt_tokens, 11)
        self.assertEqual(client.usage.completion_tokens, 4)
        self.assertEqual(client.usage.total_tokens, 15)
        call = fake.chat.completions.calls[0]
        self.assertEqual(call["model"], "test-model")
        self.assertEqual(call["response_format"], {"type": "json_object"})

    def test_from_env_requires_api_key(self) -> None:
        import os

        old = os.environ.get("LLM_API_KEY")
        os.environ["LLM_API_KEY"] = ""
        try:
            with self.assertRaises(RuntimeError):
                from_env()
        finally:
            if old is None:
                os.environ.pop("LLM_API_KEY", None)
            else:
                os.environ["LLM_API_KEY"] = old


if __name__ == "__main__":
    unittest.main()
