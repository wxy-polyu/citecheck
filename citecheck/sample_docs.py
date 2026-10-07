"""Write the small synthetic papers used by the demo and the custom question file."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

WIDGETNET = [
    [
        ("WidgetNet: A Sample Paper for Citation Checking", "title"),
        ("Abstract", "heading"),
        ("WidgetNet counts widgets in laboratory images.", "body"),
    ],
    [
        ("1 Introduction", "heading"),
        ("The main contribution is a counter called WidgetNet.", "body"),
        ("Previous work counts widgets by hand.", "body"),
    ],
    [
        ("2 Method", "heading"),
        ("WidgetNet uses a two-stage counter.", "body"),
        ("The first stage proposes regions.", "body"),
        ("The second stage labels each region as a widget.", "body"),
    ],
    [
        ("2.1 Training", "heading"),
        ("Training uses the Widget-100 dataset for 12 epochs.", "body"),
    ],
    [
        ("3 Experiments", "heading"),
        ("On Widget-100, WidgetNet reaches 91 percent accuracy.", "body"),
        ("The strongest baseline reaches 80 percent accuracy.", "body"),
        ("The efficiency experiment shows that WidgetNet uses 30 percent less memory than the baseline.", "body"),
    ],
    [
        ("4 Conclusion", "heading"),
        ("WidgetNet improves widget counting accuracy over hand counting.", "body"),
    ],
]

WIDGETNET_LITE = [
    [
        ("WidgetNet-Lite: A Smaller Sample Counter", "title"),
        ("Abstract", "heading"),
        ("WidgetNet-Lite is a smaller widget counter.", "body"),
        ("1 Introduction", "heading"),
        ("WidgetNet-Lite trades accuracy for a smaller model.", "body"),
    ],
    [
        ("2 Experiments", "heading"),
        ("On Widget-100, WidgetNet-Lite reaches 85 percent accuracy.", "body"),
        ("It uses 10 percent more memory than WidgetNet.", "body"),
    ],
]

QUESTIONS = [
    {
        "id": "contribution",
        "pdfs": ["examples/widgetnet.pdf"],
        "question": "What is the main contribution of this paper?",
        "answers": [
            "The main contribution is a counter called WidgetNet.",
            "WidgetNet",
        ],
        "evidence": ["The main contribution is a counter called WidgetNet."],
        "citations": [{"section": "1 Introduction", "page": 2}],
    },
    {
        "id": "training",
        "pdfs": ["examples/widgetnet.pdf"],
        "question": "Which dataset is used for training, and for how many epochs?",
        "answers": ["Training uses the Widget-100 dataset for 12 epochs.", "Widget-100 for 12 epochs"],
        "evidence": ["Training uses the Widget-100 dataset for 12 epochs."],
        "citations": [{"section": "2.1 Training", "page": 4}],
    },
    {
        "id": "accuracy",
        "pdfs": ["examples/widgetnet.pdf"],
        "question": "What accuracy does WidgetNet reach on Widget-100?",
        "answers": ["91 percent", "WidgetNet reaches 91 percent accuracy."],
        "evidence": ["On Widget-100, WidgetNet reaches 91 percent accuracy."],
        "citations": [{"section": "3 Experiments", "page": 5}],
    },
    {
        "id": "baseline",
        "pdfs": ["examples/widgetnet.pdf"],
        "question": "What accuracy does the strongest baseline reach?",
        "answers": ["80 percent", "The strongest baseline reaches 80 percent accuracy."],
        "evidence": ["The strongest baseline reaches 80 percent accuracy."],
        "citations": [{"section": "3 Experiments", "page": 5}],
    },
    {
        "id": "efficiency",
        "pdfs": ["examples/widgetnet.pdf"],
        "question": "Which experiment supports the claim that WidgetNet is more memory-efficient?",
        "answers": [
            "The efficiency experiment shows that WidgetNet uses 30 percent less memory than the baseline."
        ],
        "evidence": [
            "The efficiency experiment shows that WidgetNet uses 30 percent less memory than the baseline."
        ],
        "citations": [{"section": "3 Experiments", "page": 5}],
    },
    {
        "id": "first-stage",
        "pdfs": ["examples/widgetnet.pdf"],
        "question": "What does the first stage of WidgetNet do?",
        "answers": ["The first stage proposes regions."],
        "evidence": ["The first stage proposes regions."],
        "citations": [{"section": "2 Method", "page": 3}],
    },
    {
        "id": "second-stage",
        "pdfs": ["examples/widgetnet.pdf"],
        "question": "What does the second stage of WidgetNet do?",
        "answers": ["The second stage labels each region as a widget."],
        "evidence": ["The second stage labels each region as a widget."],
        "citations": [{"section": "2 Method", "page": 3}],
    },
    {
        "id": "versus-hand",
        "pdfs": ["examples/widgetnet.pdf"],
        "question": "How does WidgetNet differ from counting widgets by hand?",
        "answers": [
            "Previous work counts widgets by hand. WidgetNet uses a two-stage counter."
        ],
        "evidence": [
            "Previous work counts widgets by hand.",
            "WidgetNet uses a two-stage counter.",
        ],
        "citations": [
            {"section": "1 Introduction", "page": 2},
            {"section": "2 Method", "page": 3},
        ],
    },
    {
        "id": "conclusion",
        "pdfs": ["examples/widgetnet.pdf"],
        "question": "What does the conclusion say about hand counting?",
        "answers": ["WidgetNet improves widget counting accuracy over hand counting."],
        "evidence": ["WidgetNet improves widget counting accuracy over hand counting."],
        "citations": [{"section": "4 Conclusion", "page": 6}],
    },
    {
        "id": "missing-gpu",
        "pdfs": ["examples/widgetnet.pdf"],
        "question": "Which GPU is used to train WidgetNet?",
        "answers": [
            "The retrieved evidence does not support an answer to this question.",
            "The paper does not report the GPU.",
        ],
        "evidence": [],
        "citations": [],
    },
    {
        "id": "lite-accuracy",
        "pdfs": ["examples/widgetnet_lite.pdf"],
        "question": "What accuracy does WidgetNet-Lite reach on Widget-100?",
        "answers": ["85 percent", "WidgetNet-Lite reaches 85 percent accuracy."],
        "evidence": ["On Widget-100, WidgetNet-Lite reaches 85 percent accuracy."],
        "citations": [{"section": "2 Experiments", "page": 2}],
    },
    {
        "id": "compare-accuracy",
        "pdfs": ["examples/widgetnet.pdf", "examples/widgetnet_lite.pdf"],
        "question": "Do WidgetNet and WidgetNet-Lite report the same accuracy on Widget-100?",
        "answers": [
            "No. WidgetNet reaches 91 percent accuracy and WidgetNet-Lite reaches 85 percent accuracy."
        ],
        "evidence": [
            "On Widget-100, WidgetNet reaches 91 percent accuracy.",
            "On Widget-100, WidgetNet-Lite reaches 85 percent accuracy.",
        ],
        "citations": [
            {"section": "3 Experiments", "page": 5},
            {"section": "2 Experiments", "page": 2},
        ],
    },
    {
        "id": "compare-memory",
        "pdfs": ["examples/widgetnet.pdf", "examples/widgetnet_lite.pdf"],
        "question": "How do the two papers describe memory use?",
        "answers": [
            "WidgetNet uses 30 percent less memory than the baseline. WidgetNet-Lite uses 10 percent more memory than WidgetNet."
        ],
        "evidence": [
            "The efficiency experiment shows that WidgetNet uses 30 percent less memory than the baseline.",
            "It uses 10 percent more memory than WidgetNet.",
        ],
        "citations": [
            {"section": "3 Experiments", "page": 5},
            {"section": "2 Experiments", "page": 2},
        ],
    },
]


def write_pdf(path: Path, pages: list[list[tuple[str, str]]]) -> None:
    import pymupdf

    fonts = {"title": 20, "heading": 16, "body": 12}
    document = pymupdf.open()
    for page_lines in pages:
        page = document.new_page()
        y = 72
        for text, role in page_lines:
            size = fonts[role]
            page.insert_text((72, y), text, fontsize=size)
            y += size + 12
    path.parent.mkdir(parents=True, exist_ok=True)
    document.save(path)
    document.close()


def write_examples(root: Path | None = None) -> Path:
    """Write both sample PDFs and examples/custom_questions.json."""
    root = root or ROOT
    examples = root / "examples"
    examples.mkdir(parents=True, exist_ok=True)
    write_pdf(examples / "widgetnet.pdf", WIDGETNET)
    write_pdf(examples / "widgetnet_lite.pdf", WIDGETNET_LITE)
    destination = examples / "custom_questions.json"
    destination.write_text(json.dumps(QUESTIONS, indent=2) + "\n", encoding="utf-8")
    return destination


def main() -> None:
    path = write_examples()
    print(f"Wrote sample papers and {path}")


if __name__ == "__main__":
    main()
