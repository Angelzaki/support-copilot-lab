from __future__ import annotations

import math
import re
from collections import Counter
from pathlib import Path

TOKEN = re.compile(r"[a-zA-ZáéíóúñÁÉÍÓÚÑ0-9]+")
STOP = {"politica", "política", "cual", "cuál", "que", "qué", "como", "cómo", "para", "sobre"}


def tokenize(text: str) -> list[str]:
    return [t.lower() for t in TOKEN.findall(text)]


def load_docs(docs_dir: Path) -> list[dict]:
    docs = []
    for path in sorted(docs_dir.glob("*.txt")):
        docs.append({"id": path.stem, "text": path.read_text(encoding="utf-8")})
    return docs


class SupportRag:
    def __init__(self, docs_dir: Path, min_score: float = 0.12, min_overlap: float = 0.34):
        self.docs = load_docs(docs_dir)
        self.min_score = min_score
        self.min_overlap = min_overlap
        self._build()

    def _build(self) -> None:
        tokenized = [tokenize(d["text"]) for d in self.docs]
        df: Counter[str] = Counter()
        for tokens in tokenized:
            df.update(set(tokens))
        n = len(tokenized) or 1
        self.idf = {t: math.log((n + 1) / (f + 1)) + 1.0 for t, f in df.items()}
        self.vectors = []
        for tokens in tokenized:
            tf = Counter(tokens)
            length = len(tokens) or 1
            self.vectors.append({t: (c / length) * self.idf[t] for t, c in tf.items()})

    def ask(self, question: str) -> dict:
        if not self.docs:
            return self._escalate(question, "corpus vacío")
        q_tokens = tokenize(question)
        tf = Counter(q_tokens)
        length = len(q_tokens) or 1
        q_vec = {t: (c / length) * self.idf.get(t, 0.0) for t, c in tf.items()}
        ranked = []
        for doc, vec in zip(self.docs, self.vectors):
            keys = set(q_vec) | set(vec)
            if not keys:
                score = 0.0
            else:
                dot = sum(q_vec.get(x, 0.0) * vec.get(x, 0.0) for x in keys)
                na = math.sqrt(sum(v * v for v in q_vec.values()) or 1)
                nb = math.sqrt(sum(v * v for v in vec.values()) or 1)
                score = dot / (na * nb)
            ranked.append((score, doc))
        ranked.sort(key=lambda x: x[0], reverse=True)
        top_score, top = ranked[0]
        content = [t for t in q_tokens if t not in STOP and len(t) > 3]
        overlap = 0.0
        if content:
            ctx = set(tokenize(top["text"]))
            overlap = sum(1 for t in content if t in ctx) / len(content)
        if top_score < self.min_score or overlap < self.min_overlap:
            return self._escalate(question, "sin evidencia suficiente")

        sentences = [s.strip() for s in top["text"].replace("\n", " ").split(".") if s.strip()]
        qset = set(content)
        ranked_s = sorted(sentences, key=lambda s: sum(1 for t in qset if t in s.lower()), reverse=True)
        answer = (ranked_s[0] if ranked_s else top["text"][:180]) + "."
        return {
            "answer": answer,
            "citations": [top["id"]],
            "score": round(top_score, 4),
            "overlap": round(overlap, 4),
            "escalated": False,
            "status": "answered",
        }

    def _escalate(self, question: str, reason: str) -> dict:
        return {
            "answer": "No tengo evidencia suficiente en la base de soporte. Escalado a un agente humano.",
            "citations": [],
            "score": 0.0,
            "overlap": 0.0,
            "escalated": True,
            "status": "escalated",
            "reason": reason,
            "question": question,
        }
