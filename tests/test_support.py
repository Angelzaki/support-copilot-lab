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


def test_a05_excepcion_temporal_no_falso_escalate():
    rag = SupportRag(DOCS)
    result = rag.ask("¿Cuántos días puede durar una excepción temporal al límite?")
    assert not result["escalated"]
    assert "15" in result["answer"]
    assert "sop_limites" in result["citations"]


def test_a07_elige_frase_del_comite():
    rag = SupportRag(DOCS)
    result = rag.ask("¿Quién aprueba si se excede el límite comercial?")
    assert not result["escalated"]
    assert "comité" in result["answer"].lower() or "comite" in result["answer"].lower()
    assert "250" not in result["answer"]


def test_vocab_trap_escala():
    rag = SupportRag(DOCS)
    result = rag.ask("¿Cuál es el límite de vacaciones comerciales por cuenta?")
    assert result["escalated"] is True


def test_paraphrase_clave_chat():
    rag = SupportRag(DOCS)
    result = rag.ask("¿Puedo pedir la clave nueva por el chat de soporte?")
    assert not result["escalated"]
    assert "chat" in result["answer"].lower()
