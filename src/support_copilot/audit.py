from __future__ import annotations

import json
import time
from pathlib import Path


class AuditLog:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")

    def add(self, payload: dict) -> None:
        rows = json.loads(self.path.read_text(encoding="utf-8"))
        rows.append({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), **payload})
        self.path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    def all(self) -> list[dict]:
        return json.loads(self.path.read_text(encoding="utf-8"))
