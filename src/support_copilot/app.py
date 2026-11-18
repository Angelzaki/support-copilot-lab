from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from support_copilot.audit import AuditLog
from support_copilot.guard import firewall_enabled, screen
from support_copilot.metrics import compute_stats
from support_copilot.rag import SupportRag

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = Path(os.getenv("SUPPORT_COPILOT_DATA", str(ROOT / "data")))
RAG = SupportRag(ROOT / "samples" / "docs")
AUDIT = AuditLog(DATA_DIR / "audit.json")
TEMPLATES = Jinja2Templates(directory=str(ROOT / "templates"))

app = FastAPI(title="support-copilot-lab")
app.mount("/static", StaticFiles(directory=str(ROOT / "static")), name="static")


def _context(request: Request, result: dict | None, question: str = "") -> dict:
    rows = AUDIT.all()
    return {
        "request": request,
        "result": result,
        "question": question,
        "history": list(reversed(rows))[:20],
        "stats": compute_stats(rows),
        "firewall": firewall_enabled(),
    }


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return TEMPLATES.TemplateResponse(request, "index.html", _context(request, None))


@app.post("/ask", response_class=HTMLResponse)
def ask(request: Request, question: str = Form(...)):
    result = screen(question) or RAG.ask(question)
    AUDIT.add({"question": question, **result})
    return TEMPLATES.TemplateResponse(request, "index.html", _context(request, result, question))


@app.post("/clear")
def clear():
    AUDIT.path.write_text("[]", encoding="utf-8")
    return RedirectResponse("/", status_code=303)


@app.get("/api/stats")
def api_stats():
    return JSONResponse(compute_stats(AUDIT.all()))


@app.get("/health")
def health():
    return {"status": "ok", "docs": len(RAG.docs)}
