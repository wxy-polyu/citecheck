"""Ask one question about one or more paper PDFs."""

from __future__ import annotations

import argparse
from pathlib import Path

from citecheck.agent import SYSTEMS, answer_question
from citecheck.ingest import parse_pdfs
from citecheck.llm import from_env


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Ask a question about paper PDFs.")
    parser.add_argument("--pdf", action="append", required=True, help="PDF path. Repeat for more papers.")
    parser.add_argument("--question", required=True)
    parser.add_argument("--system", default="full", choices=sorted(SYSTEMS))
    args = parser.parse_args(argv)

    chunks = parse_pdfs([Path(path) for path in args.pdf])
    result = answer_question(args.question, chunks, from_env(), system=args.system)
    print(result.answer)
    print()
    for claim in result.claims:
        location = claim.section or "no citation"
        if claim.page is not None:
            location = f"{location}, p. {claim.page}"
        print(f"- [{claim.label}] {claim.text} ({location})")
    print()
    print(
        f"system={result.system} steps={result.steps} "
        f"latency_s={result.latency_s:.1f} tokens={result.prompt_tokens + result.completion_tokens}"
    )


if __name__ == "__main__":
    main()
