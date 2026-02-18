from __future__ import annotations

import json
from collections import Counter

from code_review_assistant.models import ReviewReport


def to_json(report: ReviewReport) -> str:
    return json.dumps(report.to_dict(), indent=2)


def to_markdown(report: ReviewReport) -> str:
    lines: list[str] = []
    lines.append(f"# Code Review Report: {report.target}")
    lines.append("")

    sev = Counter([item.severity for item in report.findings])
    lines.append("## Summary")
    lines.append(f"- Total findings: {len(report.findings)}")
    lines.append(f"- High: {sev.get('high', 0)}")
    lines.append(f"- Medium: {sev.get('medium', 0)}")
    lines.append(f"- Low: {sev.get('low', 0)}")
    lines.append("")

    if report.ai_summary:
        lines.append("## AI Insights")
        lines.append(report.ai_summary)
        lines.append("")

    lines.append("## Findings")
    if not report.findings:
        lines.append("No issues found.")
    else:
        for item in report.findings:
            location = f"{item.file_path}:{item.line}" if item.line else item.file_path
            lines.append(f"- [{item.severity.upper()}] `{location}` `{item.tool}`: {item.message}")
            if item.suggestion:
                lines.append(f"  Suggestion: {item.suggestion}")

    return "\n".join(lines).strip() + "\n"
