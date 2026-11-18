from __future__ import annotations

import json
from pathlib import Path

from support_copilot.rag import SupportRag


def load_asks(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def evaluate(rag: SupportRag, asks: list[dict]) -> dict:
    rows = []
    for ask in asks:
        result = rag.ask(ask["question"])
        got = "escalate" if result["escalated"] else "answer"
        ok = got == ask["expect"]
        if ok and got == "answer":
            ok = ask.get("source") in result["citations"] and ask.get("contains", "") in result["answer"]
        rows.append(
            {
                "id": ask["id"],
                "question": ask["question"],
                "expect": ask["expect"],
                "got": got,
                "score": result["score"],
                "overlap": result["overlap"],
                "citations": result["citations"],
                "ok": ok,
            }
        )
    expected_answer = [r for r in rows if r["expect"] == "answer"]
    expected_escalate = [r for r in rows if r["expect"] == "escalate"]
    return {
        "total": len(rows),
        "passed": sum(1 for r in rows if r["ok"]),
        "grounded_ok": sum(1 for r in expected_answer if r["ok"]),
        "grounded_total": len(expected_answer),
        "escalate_ok": sum(1 for r in expected_escalate if r["ok"]),
        "escalate_total": len(expected_escalate),
        "rows": rows,
    }


def to_markdown(report: dict) -> str:
    lines = [
        "| id | esperado | obtenido | score | overlap | fuente | ok |",
        "|----|----------|----------|-------|---------|--------|----|",
    ]
    for r in report["rows"]:
        src = ", ".join(r["citations"]) or "-"
        lines.append(
            f"| {r['id']} | {r['expect']} | {r['got']} | {r['score']} | {r['overlap']} | {src} | {'sí' if r['ok'] else 'no'} |"
        )
    return "\n".join(lines)
