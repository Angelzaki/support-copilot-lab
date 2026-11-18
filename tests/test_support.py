from pathlib import Path

from support_copilot.rag import SupportRag

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "samples" / "docs"


def test_answers_with_citation():
    rag = SupportRag(DOCS)
    result = rag.ask("¿Cuál es el límite comercial?")
    assert not result["escalated"]
    assert result["citations"]
    assert "250" in result["answer"]


def test_escalates_unknown():
    rag = SupportRag(DOCS)
    result = rag.ask("política de viajes interplanetarios 2099")
    assert result["escalated"] is True
