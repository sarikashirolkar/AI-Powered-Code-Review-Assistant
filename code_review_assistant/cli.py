from __future__ import annotations

import argparse
import sys
from pathlib import Path

from code_review_assistant.models import ReviewReport
from code_review_assistant.reporting.formatter import to_json, to_markdown
from code_review_assistant.review_engine import review_github_pr, review_local_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AI-Powered Code Review Assistant")
    subparsers = parser.add_subparsers(dest="command", required=True)

    local_cmd = subparsers.add_parser("review-path", help="Review local files")
    local_cmd.add_argument("--path", default=".", help="File or folder to review")
    local_cmd.add_argument("--format", choices=["markdown", "json"], default="markdown")
    local_cmd.add_argument("--output", help="Optional output report path")
    local_cmd.add_argument("--use-ai", action="store_true", help="Enable OpenAI review summary")
    local_cmd.add_argument(
        "--complexity-threshold",
        default="C",
        choices=["A", "B", "C", "D", "E", "F"],
        help="Minimum complexity rank to include",
    )

    pr_cmd = subparsers.add_parser("review-pr", help="Review a GitHub pull request")
    pr_cmd.add_argument("--repo", required=True, help="Repo in owner/name format")
    pr_cmd.add_argument("--pr-number", type=int, required=True, help="Pull request number")
    pr_cmd.add_argument("--format", choices=["markdown", "json"], default="markdown")
    pr_cmd.add_argument("--output", help="Optional output report path")
    pr_cmd.add_argument("--use-ai", action="store_true", help="Enable OpenAI review summary")

    return parser


def review_path(args: argparse.Namespace) -> ReviewReport:
    return review_local_path(
        path=args.path,
        complexity_threshold=args.complexity_threshold,
        use_ai=args.use_ai,
    )


def review_pr(args: argparse.Namespace) -> ReviewReport:
    return review_github_pr(repo=args.repo, pr_number=args.pr_number, use_ai=args.use_ai)


def render_report(report: ReviewReport, fmt: str) -> str:
    if fmt == "json":
        return to_json(report)
    return to_markdown(report)


def maybe_write_output(content: str, output_path: str | None) -> None:
    if not output_path:
        return
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "review-path":
            report = review_path(args)
        elif args.command == "review-pr":
            report = review_pr(args)
        else:
            parser.error(f"Unsupported command: {args.command}")
            return 2
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    output = render_report(report, args.format)
    print(output)
    maybe_write_output(output, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
