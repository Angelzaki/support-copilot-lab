from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from support_copilot.audit import AuditLog
from support_copilot.rag import SupportRag

ROOT = Path(__file__).resolve().parents[2]
RAG = SupportRag(ROOT / "samples" / "docs")
AUDIT = AuditLog(ROOT / "data" / "audit.json")
TEMPLATES = Jinja2Templates(directory=str(ROOT / "templates"))

app = FastAPI(title="support-copilot-lab")
app.mount("/static", StaticFiles(directory=str(ROOT / "static")), name="static")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return TEMPLATES.TemplateResponse(
        "index.html",
        {
            "request": request,
            "result": None,
            "history": list(reversed(AUDIT.all()))[:20],
        },
    )


@app.post("/ask", response_class=HTMLResponse)
def ask(request: Request, question: str = Form(...)):
    result = RAG.ask(question)
    AUDIT.add({"question": question, **result})
    return TEMPLATES.TemplateResponse(
        "index.html",
        {
            "request": request,
            "result": result,
            "question": question,
            "history": list(reversed(AUDIT.all()))[:20],
        },
    )


@app.post("/clear")
def clear():
    (ROOT / "data" / "audit.json").write_text("[]", encoding="utf-8")
    return RedirectResponse("/", status_code=303)
