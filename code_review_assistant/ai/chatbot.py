from __future__ import annotations

import json

from openai import OpenAI

from code_review_assistant.config import Settings
from code_review_assistant.models import ReviewReport


CHAT_SYSTEM_PROMPT = (
    "You are an expert code review assistant. Use the provided report context to answer "
    "developer questions with practical, code-focused recommendations. Keep answers concise."
)


def ask_review_bot(settings: Settings, report: ReviewReport, question: str) -> str:
    if not settings.openai_api_key:
        return "OPENAI_API_KEY not configured. Bot is unavailable."

    client = OpenAI(api_key=settings.openai_api_key)
    context = {
        "target": report.target,
        "total_findings": len(report.findings),
        "findings": [finding.to_dict() for finding in report.findings[:80]],
        "ai_summary": report.ai_summary,
        "metadata": report.metadata,
    }

    response = client.responses.create(
        model=settings.openai_model,
        input=[
            {"role": "system", "content": CHAT_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    "Code review context:\n"
                    f"{json.dumps(context)}\n\n"
                    f"Developer question: {question}"
                ),
            },
        ],
        temperature=0.2,
    )

    return (response.output_text or "No response generated.").strip()
