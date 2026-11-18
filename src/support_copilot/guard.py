from __future__ import annotations

import os


def firewall_enabled() -> bool:
    return os.getenv("SUPPORT_COPILOT_FIREWALL", "0") == "1"


def screen(question: str) -> dict | None:
    """Devuelve un resultado 'blocked' si prompt-firewall rechaza la pregunta.

    prompt-firewall es opcional: sin el paquete instalado o con el flag
    apagado, la función devuelve None y el flujo sigue sin cambios.
    """
    if not firewall_enabled():
        return None
    try:
        from prompt_firewall.rules import inspect
    except ImportError:
        return None
    verdict = inspect(question)
    if verdict.allowed:
        return None
    return {
        "answer": "La consulta fue bloqueada por la capa de seguridad y derivada a revisión humana.",
        "citations": [],
        "score": 0.0,
        "overlap": 0.0,
        "escalated": True,
        "status": "blocked",
        "reason": "prompt-firewall: " + ", ".join(verdict.matched),
        "question": question,
    }
