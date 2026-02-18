from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from code_review_assistant.ai.reviewer import generate_ai_review
from code_review_assistant.analyzers.complexity import run_complexity
from code_review_assistant.analyzers.heuristics import run_bug_risk_heuristics
from code_review_assistant.analyzers.static import run_ruff
from code_review_assistant.config import get_settings
from code_review_assistant.github.client import GitHubClient
from code_review_assistant.models import ReviewReport


def review_local_path(path: str, complexity_threshold: str = "C", use_ai: bool = False) -> ReviewReport:
    report = ReviewReport(target=str(Path(path).resolve()))
    report.add_findings(run_ruff(path))
    report.add_findings(run_complexity(path, min_grade=complexity_threshold))
    report.add_findings(run_bug_risk_heuristics(path))

    if use_ai:
        settings = get_settings()
        report.ai_summary = generate_ai_review(settings=settings, findings=report.findings)

    return report


def review_github_pr(repo: str, pr_number: int, use_ai: bool = False) -> ReviewReport:
    settings = get_settings()
    gh = GitHubClient(token=settings.github_token)
    files = gh.fetch_pr_files(repo=repo, pr_number=pr_number)

    report = ReviewReport(
        target=f"https://github.com/{repo}/pull/{pr_number}",
        metadata={"files_changed": len(files)},
    )

    if use_ai:
        report.ai_summary = generate_ai_review(settings=settings, findings=[], changed_files=files)

    return report


def review_code_snippet(
    code: str,
    filename: str = "snippet.py",
    complexity_threshold: str = "C",
    use_ai: bool = False,
) -> ReviewReport:
    if not code.strip():
        raise ValueError("Code snippet is empty.")

    with TemporaryDirectory(prefix="code_review_snippet_") as tmp_dir:
        snippet_path = Path(tmp_dir) / filename
        snippet_path.write_text(code, encoding="utf-8")

        report = ReviewReport(
            target=f"in-memory snippet ({filename})",
            metadata={"source": "pasted_code"},
        )
        report.add_findings(run_ruff(str(snippet_path)))
        report.add_findings(run_complexity(str(snippet_path), min_grade=complexity_threshold))
        report.add_findings(run_bug_risk_heuristics(str(snippet_path)))

        if use_ai:
            settings = get_settings()
            report.ai_summary = generate_ai_review(settings=settings, findings=report.findings)

        return report
