from __future__ import annotations

import argparse
import json
from pathlib import Path

import uvicorn

from support_copilot.experiment import evaluate, load_asks, to_markdown
from support_copilot.rag import SupportRag

ROOT = Path(__file__).resolve().parents[2]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="support-copilot")
    sub = parser.add_subparsers(dest="cmd", required=True)
    ask = sub.add_parser("ask")
    ask.add_argument("question")
    exp = sub.add_parser("experiment")
    exp.add_argument("--file", default=str(ROOT / "samples" / "asks.jsonl"))
    exp.add_argument(
        "--extended",
        action="store_true",
        help="Usa samples/asks_extended.jsonl (paráfrasis + trampas de vocabulario)",
    )
    exp.add_argument("--format", choices=["json", "md"], default="md")
    serve = sub.add_parser("serve")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8012)
    args = parser.parse_args(argv)

    rag = SupportRag(ROOT / "samples" / "docs")
    if args.cmd == "ask":
        print(json.dumps(rag.ask(args.question), ensure_ascii=False, indent=2))
        return 0
    if args.cmd == "experiment":
        asks_path = Path(args.file)
        if args.extended:
            asks_path = ROOT / "samples" / "asks_extended.jsonl"
        report = evaluate(rag, load_asks(asks_path))
        if args.format == "json":
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print(to_markdown(report))
            print(
                f"\ngrounded {report['grounded_ok']}/{report['grounded_total']} · "
                f"escalate {report['escalate_ok']}/{report['escalate_total']} · "
                f"total {report['passed']}/{report['total']}"
            )
        return 0 if report["passed"] == report["total"] else 1
    if args.cmd == "serve":
        uvicorn.run("support_copilot.app:app", host=args.host, port=args.port)
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
