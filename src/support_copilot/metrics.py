from __future__ import annotations

from collections import Counter


def compute_stats(rows: list[dict]) -> dict:
    total = len(rows)
    grounded = [r for r in rows if r.get("status") == "answered"]
    escalated = [r for r in rows if r.get("status") == "escalated"]
    blocked = [r for r in rows if r.get("status") == "blocked"]
    scores = [float(r.get("score", 0.0)) for r in grounded]
    sources: Counter[str] = Counter()
    for r in grounded:
        sources.update(r.get("citations", []))
    return {
        "total": total,
        "grounded": len(grounded),
        "escalated": len(escalated),
        "blocked": len(blocked),
        "escalate_rate": round((len(escalated) + len(blocked)) / total, 4) if total else 0.0,
        "avg_confidence": round(sum(scores) / len(scores), 4) if scores else 0.0,
        "top_sources": sources.most_common(3),
    }
