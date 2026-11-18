from __future__ import annotations

import math
import re
from collections import Counter
from pathlib import Path

TOKEN = re.compile(r"[a-zA-ZáéíóúñÁÉÍÓÚÑ0-9]+")
STOP = {
    "el",
    "la",
    "los",
    "las",
    "un",
    "una",
    "de",
    "del",
    "al",
    "en",
    "por",
    "con",
    "se",
    "si",
    "es",
    "no",
    "politica",
    "cual",
    "que",
    "como",
    "para",
    "sobre",
    "cuanto",
    "cuantos",
    "cuantas",
    "quien",
    "sop",
}


def _fold(text: str) -> str:
    table = str.maketrans("áéíóúüñÁÉÍÓÚÜÑ", "aeiouunAEIOUUN")
    return text.translate(table).lower()


# Sinónimos de paráfrasis frecuentes (antes de stem).
SYNONYMS = {
    "clave": "contrasena",
    "claves": "contrasena",
    "password": "contrasena",
    "descontar": "descuento",
    "descuenta": "descuento",
    "descontado": "descuento",
    "porcentaje": "descuento",
    "autorizar": "aprob",
    "autorizarlo": "aprob",
    "autorizacion": "aprob",
    "autoriza": "aprob",
    "tope": "limit",
    "restablecer": "reset",
    "restablezco": "reset",
    "confirmo": "verific",
    "confirmar": "verific",
    "paso": "exced",
    "pase": "exced",
}

# Términos de la pregunta que no están en el SOP pero no bastan para escalar.
SOFT_MISS = {
    "soporte",
    "pedir",
    "nueva",
    "nuevo",
    "tiempo",
    "maximo",
    "aceptan",
    "aceptar",
    "debe",
    "paso",
    "puedo",
    "puede",
    "pueden",
    "hasta",
    "tambien",
    "solo",
    "basta",
    "oficina",
    "interno",
    "area",
    "durar",
    "duracion",
    "tras",
    "firmar",
    "firma",
    "habil",
    "habiles",
    "activa",
    "activar",
    "chat",
}


def stem(token: str) -> str:
    t = _fold(token)
    if t in SYNONYMS:
        t = SYNONYMS[t]
    if len(t) <= 3:
        return t
    if t.startswith("aprob") or t.startswith("aprue") or t.startswith("autor"):
        return "aprob"
    if t.startswith("exced"):
        return "exced"
    if t.startswith("excepc"):
        return "excepc"
    if t.startswith("temp"):
        return "temp"
    if t.startswith("limit"):
        return "limit"
    if t.startswith("contrasen") or t.startswith("password"):
        return "contrasena"
    if t.startswith("descuent") or t.startswith("descont"):
        return "descuento"
    if t.startswith("verific") or t.startswith("confirm"):
        return "verific"
    if t.startswith("vacacion"):
        return "vacacion"
    # Sufijos largos solo sobre la forma original (evitar vacaciones→vacacion→vaca).
    for suf in ("mente", "ciones", "cion", "adores", "ador", "antes", "ante"):
        if t.endswith(suf) and len(t) - len(suf) >= 4:
            return t[: -len(suf)]
    if t.endswith("es") and len(t) > 5:
        return t[:-2]
    if t.endswith("s") and len(t) > 4 and not t.endswith("us"):
        return t[:-1]
    return t


def tokenize(text: str) -> list[str]:
    return [stem(t) for t in TOKEN.findall(text)]


def content_tokens(text: str) -> list[str]:
    out = []
    for raw in TOKEN.findall(text):
        folded = _fold(raw)
        keep_code = any(ch.isdigit() for ch in folded)
        if folded in STOP or (len(folded) <= 2 and not keep_code):
            continue
        s = stem(raw)
        if s in STOP or (len(s) <= 2 and not keep_code):
            continue
        out.append(s)
    return out


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
        content = content_tokens(question)
        ctx = set(tokenize(top["text"]))
        # Soft tokens no cuentan para overlap (evitan falsos escalate por "soporte"/"pedir").
        core = [t for t in content if t not in SOFT_MISS]
        overlap = 0.0
        if core:
            overlap = sum(1 for t in core if t in ctx) / len(core)
        elif content:
            overlap = sum(1 for t in content if t in ctx) / len(content)
        # Vocabulario del SOP en la pregunta + tema ajeno (vacaciones, wifi, etc.)
        hard_miss = [
            t for t in content if t not in ctx and t not in SOFT_MISS and len(t) >= 5
        ]
        if hard_miss:
            return self._escalate(question, "tema fuera del SOP (términos no cubiertos)")
        if top_score < self.min_score or overlap < self.min_overlap:
            return self._escalate(question, "sin evidencia suficiente")

        sentences = []
        for s in re.split(r"[.\n]+", top["text"]):
            s = s.strip()
            if len(s) < 28:
                continue
            if _fold(s).startswith("sop"):
                continue
            sentences.append(s)
        if not sentences:
            sentences = [s.strip() for s in re.split(r"[.\n]+", top["text"]) if s.strip()]

        qset = set(content)
        # En cuántas oraciones aparece cada término de la pregunta
        sent_toks = [tokenize(s) for s in sentences]
        df_sent: Counter[str] = Counter()
        for toks in sent_toks:
            df_sent.update(set(toks) & qset)

        # Términos de acción suelen distinguir la frase correcta del título/definición.
        ACTION = {
            "aprob",
            "exced",
            "excepc",
            "requier",
            "super",
            "verific",
            "envi",
            "aplica",
            "activ",
            "bloque",
            "descuento",
            "contrasena",
        }

        def sentence_score(sentence: str, stoks: list[str]) -> float:
            hits = [t for t in set(stoks) if t in qset]
            if not hits:
                return -1.0
            specificity = sum(1.0 / df_sent.get(t, 1) for t in hits)
            action_bonus = 2.0 * sum(1 for t in hits if t in ACTION)
            return action_bonus + len(hits) + 1.25 * specificity

        scored = [(sentence_score(s, toks), s) for s, toks in zip(sentences, sent_toks)]
        scored.sort(key=lambda x: x[0], reverse=True)
        best = scored[0][1] if scored else top["text"][:180]
        answer = best if best.endswith(".") else best + "."
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
