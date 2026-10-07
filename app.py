"""Demo page: upload papers, ask a question, and read the cited answer."""

from __future__ import annotations

import hashlib
import tempfile
from pathlib import Path

import streamlit as st

from citecheck.agent import answer_question
from citecheck.ingest import parse_pdfs
from citecheck.llm import ROOT, from_env
from citecheck.retrieve import Retriever
from citecheck.sample_docs import write_examples

SYSTEM_LABELS = {
    "full": "CiteCheck",
    "b3": "B3 planner + retrieval, no verifier",
    "b2": "B2 single-pass RAG",
    "b1": "B1 prompt only",
    "no_planner": "Ablation: no planner",
    "embedding_only": "Ablation: embedding only",
    "no_verifier": "Ablation: no verifier",
}


st.set_page_config(page_title="CiteCheck", layout="wide")
st.title("CiteCheck")
st.caption("Ask a question about a paper and see which sentences the retrieved passages support.")


def main() -> None:
    with st.sidebar:
        source = st.radio("Papers", ["Sample papers", "Upload PDFs"])
        include_lite = False
        uploads = []
        if source == "Sample papers":
            include_lite = st.checkbox("Compare with WidgetNet-Lite", value=False)
        else:
            uploads = st.file_uploader("PDF", type="pdf", accept_multiple_files=True)
        system = st.selectbox(
            "System",
            list(SYSTEM_LABELS),
            format_func=lambda key: SYSTEM_LABELS[key],
        )
        question = st.text_area(
            "Question",
            value="What accuracy does WidgetNet reach on Widget-100?",
            height=100,
        )
        run = st.button("Answer", type="primary")

    if not run:
        st.info("Choose a paper, ask a question, then click Answer.")
        return
    if not question.strip():
        st.warning("Enter a question first.")
        return
    try:
        retriever = _load_retriever(source, include_lite, uploads or [])
    except Exception as exc:
        st.error(str(exc))
        return
    try:
        llm = from_env()
    except RuntimeError as exc:
        st.error(str(exc))
        return
    with st.spinner("Retrieving passages and checking each sentence..."):
        result = answer_question(
            question.strip(),
            retriever.chunks,
            llm,
            system=system,
            retriever=retriever if system != "b1" else None,
        )

    st.subheader("Answer")
    st.write(result.answer)
    st.caption(
        f"{result.steps} retrieval steps · {result.latency_s:.1f}s · "
        f"{result.prompt_tokens + result.completion_tokens} tokens"
    )

    st.subheader("Claims")
    if not result.claims:
        st.write("No claims were produced.")
    for claim in result.claims:
        if claim.label == "supported":
            page = "unknown page" if claim.page is None else f"p. {claim.page}"
            st.success(f"{claim.text}  \n{claim.paper_title} · {claim.section} · {page}")
        else:
            st.warning(f"Uncertain ({claim.verdict}): {claim.text}")

    with st.expander("Retrieved passages"):
        if not result.evidence:
            st.write("No passages were retrieved.")
        for index, chunk in enumerate(result.evidence, start=1):
            page = "unknown page" if chunk.page is None else f"p. {chunk.page}"
            st.markdown(f"**[E{index}] {chunk.paper_title} · {chunk.section} · {page}**")
            st.write(chunk.text)


def _load_retriever(source: str, include_lite: bool, uploads: list) -> Retriever:
    if source == "Sample papers":
        return _sample_retriever(include_lite)
    if not uploads:
        raise RuntimeError("Upload at least one PDF, or switch to the sample papers.")
    payloads = tuple((upload.name, upload.getvalue()) for upload in uploads)
    key = hashlib.sha256(b"".join(name.encode() + data for name, data in payloads)).hexdigest()
    return _upload_retriever(key, payloads)


@st.cache_resource(show_spinner="Indexing the sample papers...")
def _sample_retriever(include_lite: bool) -> Retriever:
    examples = ROOT / "examples"
    if not (examples / "widgetnet.pdf").exists():
        write_examples()
    paths = [examples / "widgetnet.pdf"]
    if include_lite:
        paths.append(examples / "widgetnet_lite.pdf")
    return Retriever(parse_pdfs(paths), mode="hybrid")


@st.cache_resource(show_spinner="Indexing the uploaded papers...")
def _upload_retriever(key: str, payloads: tuple[tuple[str, bytes], ...]) -> Retriever:
    del key
    directory = Path(tempfile.mkdtemp(prefix="citecheck-"))
    paths = []
    for name, data in payloads:
        safe_name = Path(name).name or "paper.pdf"
        path = directory / safe_name
        path.write_bytes(data)
        paths.append(path)
    return Retriever(parse_pdfs(paths), mode="hybrid")


if __name__ == "__main__":
    main()
else:
    main()
