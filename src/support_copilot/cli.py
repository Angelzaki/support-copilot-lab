from __future__ import annotations

import argparse
import json
from pathlib import Path

import uvicorn
from rich.console import Console

from support_copilot.rag import SupportRag

console = Console()
ROOT = Path(__file__).resolve().parents[2]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="support-copilot")
    sub = parser.add_subparsers(dest="cmd", required=True)
    ask = sub.add_parser("ask")
    ask.add_argument("question")
    serve = sub.add_parser("serve")
    serve.add_argument("--port", type=int, default=8012)
    args = parser.parse_args(argv)

    if args.cmd == "ask":
        rag = SupportRag(ROOT / "samples" / "docs")
        print(json.dumps(rag.ask(args.question), ensure_ascii=False, indent=2))
        return 0
    if args.cmd == "serve":
        uvicorn.run("support_copilot.app:app", host="127.0.0.1", port=args.port)
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
