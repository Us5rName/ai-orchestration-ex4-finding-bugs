"""CLI entry point — thin presentation layer over the SDK.

Run with ``python -m ex04 <command>``. Contains no business logic: every
command loads the SDK from config and delegates. See ``docs/PHASE5_INTEGRATION.md``.
"""

from __future__ import annotations

import argparse
import logging
import sys
import uuid
from pathlib import Path

from ex04.sdk import Ex04SDK
from ex04.shared.types_request import ComparisonRequest

logger = logging.getLogger("ex04")

DEFAULT_CONFIG = "config/setup.json"


def _build_parser() -> argparse.ArgumentParser:
    """Build the argument parser with the four subcommands."""
    parser = argparse.ArgumentParser(
        prog="ex04", description="EX04 — graph-guided bug investigation toolkit."
    )
    parser.add_argument(
        "--config", default=DEFAULT_CONFIG, help="Path to config JSON (default: %(default)s)."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_graphify = sub.add_parser("graphify", help="Extract a code graph from a codebase.")
    p_graphify.add_argument("target_path", help="Path to the target codebase.")

    p_investigate = sub.add_parser("investigate", help="Investigate a bug.")
    p_investigate.add_argument("bug_report", help="Bug description (or @path to a file).")

    p_compare = sub.add_parser("compare", help="Compare naive vs. graph-guided runs.")
    p_compare.add_argument("target_path", help="Path to the target codebase.")
    p_compare.add_argument("bug_report", help="Bug description (or @path to a file).")

    p_pipeline = sub.add_parser("pipeline", help="Run the full end-to-end pipeline.")
    p_pipeline.add_argument("target_path", help="Path to the target codebase.")
    p_pipeline.add_argument("bug_report", help="Bug description (or @path to a file).")

    for cmd, hlp in (
        ("investigate-naive", "Run naive (no-graph) investigation."),
        ("investigate-graph", "Run graph-guided investigation."),
    ):
        p = sub.add_parser(cmd, help=hlp)
        p.add_argument("bug_report", help="Bug description (or @path to a file).")
        p.add_argument("--provider", default="openai", help="LLM provider.")
        p.add_argument("--run-id", dest="run_id", default="", help="Unique run ID.")

    return parser


def _read_report(value: str) -> str:
    """Resolve a bug-report argument, expanding a leading ``@`` to file contents."""
    if value.startswith("@"):
        return Path(value[1:]).read_text(encoding="utf-8")
    return value


def _dispatch(args: argparse.Namespace, sdk: Ex04SDK) -> object:
    """Delegate a parsed command to the SDK and return its result."""
    if args.command == "graphify":
        return sdk.run_graphify(args.target_path)
    if args.command == "investigate":
        return sdk.investigate_bug(_read_report(args.bug_report))
    if args.command == "compare":
        return sdk.compare_target(args.target_path, _read_report(args.bug_report))
    if args.command == "pipeline":
        return sdk.full_pipeline(args.target_path, _read_report(args.bug_report))
    if args.command in ("investigate-naive", "investigate-graph"):
        req = ComparisonRequest(
            bug_report=_read_report(args.bug_report),
            provider=args.provider,
            run_id=args.run_id or uuid.uuid4().hex[:12],
        )
        if args.command == "investigate-naive":
            return sdk.run_naive_investigation(req)
        return sdk.run_graph_investigation(req)
    raise ValueError(f"Unknown command: {args.command}")  # pragma: no cover


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Returns a process exit code."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    args = _build_parser().parse_args(argv)
    try:
        sdk = Ex04SDK.from_config(args.config)
        result = _dispatch(args, sdk)
    except FileNotFoundError as exc:
        logger.error("File not found: %s", exc)
        return 2
    except NotImplementedError as exc:
        logger.error("Not yet available: %s", exc)
        return 3
    except Exception as exc:  # noqa: BLE001 — top-level CLI guard
        logger.exception("Command failed: %s", exc)
        return 1
    print(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
