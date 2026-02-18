from __future__ import annotations

import json

from code_review_assistant.ai.provider import generate_llm_response
from code_review_assistant.config import Settings
from code_review_assistant.models import ReviewReport


CHAT_SYSTEM_PROMPT = (
    "You are an expert code review assistant. Use the provided report context to answer "
    "developer questions with practical, code-focused recommendations. Keep answers concise."
)


def ask_review_bot(settings: Settings, report: ReviewReport, question: str) -> str:
    context = {
        "target": report.target,
        "total_findings": len(report.findings),
        "findings": [finding.to_dict() for finding in report.findings[:80]],
        "ai_summary": report.ai_summary,
        "metadata": report.metadata,
    }

    return generate_llm_response(
        settings=settings,
        system_prompt=CHAT_SYSTEM_PROMPT,
        user_prompt=(
            "Code review context:\n"
            f"{json.dumps(context)}\n\n"
            f"Developer question: {question}"
        ),
    )
