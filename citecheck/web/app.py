"""HTTP entry for the demo page."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from citecheck.agent import SYSTEMS
from citecheck.web.service import ask, get_library, index_sample, index_uploads

STATIC = Path(__file__).resolve().parent / "static"

app = FastAPI(title="CiteCheck")
app.mount("/static", StaticFiles(directory=STATIC), name="static")


class AskBody(BaseModel):
    library_id: str
    question: str
    system: str = "full"


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC / "index.html")


@app.post("/api/library")
def create_library(
    source: str = Form(...),
    include_lite: str = Form("false"),
    files: list[UploadFile] | None = File(default=None),
) -> dict:
    try:
        if source == "sample":
            library_id, outline = index_sample(_flag(include_lite))
        elif source == "upload":
            payloads = _read_uploads(files or [])
            if not payloads:
                _fail(400, "need_pdf")
            library_id, outline = index_uploads(payloads)
        else:
            _fail(400, "unknown_source")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "index_failed", "message": str(exc)},
        ) from exc
    return {"library_id": library_id, "papers": outline}


@app.post("/api/ask")
def create_answer(body: AskBody) -> dict:
    question = body.question.strip()
    if not question:
        _fail(400, "empty_question")
    if body.system not in SYSTEMS:
        _fail(400, "unknown_system")
    if get_library(body.library_id) is None:
        _fail(404, "unknown_library")
    try:
        return ask(body.library_id, question, body.system)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail={"code": "llm", "message": str(exc)}) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail={"code": "ask_failed", "message": str(exc)},
        ) from exc


def _read_uploads(files: list[UploadFile]) -> list[tuple[str, bytes]]:
    payloads: list[tuple[str, bytes]] = []
    for upload in files:
        name = upload.filename or "paper.pdf"
        if Path(name).suffix.lower() != ".pdf":
            continue
        payloads.append((name, upload.file.read()))
    return payloads


def _flag(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _fail(status: int, code: str) -> None:
    raise HTTPException(status_code=status, detail={"code": code})
