"""Configurable OpenAI-compatible language-model client."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]


@dataclass
class TokenUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens

    def add(self, prompt_tokens: int, completion_tokens: int) -> None:
        self.prompt_tokens += prompt_tokens
        self.completion_tokens += completion_tokens


@dataclass
class LLMClient:
    """Chat client that records token use for later cost reporting."""

    model: str
    client: object
    usage: TokenUsage = field(default_factory=TokenUsage)

    def complete(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0.0,
        json_mode: bool = False,
    ) -> str:
        kwargs: dict = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        response = self.client.chat.completions.create(**kwargs)
        usage = getattr(response, "usage", None)
        if usage is not None:
            self.usage.add(
                int(getattr(usage, "prompt_tokens", 0) or 0),
                int(getattr(usage, "completion_tokens", 0) or 0),
            )
        content = response.choices[0].message.content
        return content or ""

    def complete_json(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0.0,
    ) -> dict:
        """Ask for a JSON object. Retry without JSON mode if the server rejects it."""
        try:
            text = self.complete(messages, temperature=temperature, json_mode=True)
        except Exception as exc:
            if "response_format" not in str(exc).lower() and "json" not in str(exc).lower():
                raise
            text = self.complete(messages, temperature=temperature, json_mode=False)
        return parse_json(text)


def parse_json(text: str) -> dict:
    """Parse a JSON object, including a markdown fence or surrounding text."""
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        value = json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        if match is None:
            raise ValueError(f"Model did not return JSON: {cleaned[:300]}")
        value = json.loads(match.group(0))
    if not isinstance(value, dict):
        raise ValueError("Model JSON was not an object.")
    return value


def load_settings() -> dict[str, str]:
    """Read LLM settings from the environment and the repo-root `.env`."""
    load_dotenv(ROOT / ".env")
    return {
        "base_url": os.getenv("LLM_BASE_URL", "https://api.openai.com/v1").strip(),
        "api_key": os.getenv("LLM_API_KEY", "").strip(),
        "model": os.getenv("LLM_MODEL", "gpt-4o-mini").strip(),
    }


def from_env() -> LLMClient:
    """Build a client from `LLM_BASE_URL`, `LLM_API_KEY`, and `LLM_MODEL`."""
    settings = load_settings()
    if not settings["api_key"]:
        raise RuntimeError(
            "LLM_API_KEY is empty. Copy .env.example to .env and set the key."
        )
    from openai import OpenAI

    client = OpenAI(base_url=settings["base_url"], api_key=settings["api_key"])
    return LLMClient(model=settings["model"], client=client)
