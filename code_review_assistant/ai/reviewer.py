from __future__ import annotations

import json

from openai import OpenAI

from code_review_assistant.config import Settings
from code_review_assistant.models import Finding


SYSTEM_PROMPT = (
    "You are a senior staff engineer performing code review. "
    "Focus on correctness, maintainability, performance, and security. "
    "Respond with concise markdown bullet points and concrete fixes."
)


def generate_ai_review(
    settings: Settings,
    findings: list[Finding],
    changed_files: list[dict] | None = None,
) -> str:
    if not settings.openai_api_key:
        return "OPENAI_API_KEY not configured. AI review skipped."

    client = OpenAI(api_key=settings.openai_api_key)

    finding_payload = [f.to_dict() for f in findings[:60]]
    changed_payload = (changed_files or [])[:20]

    user_prompt = {
        "summary": (
            "Review the static findings and changed files. "
            "Prioritize high-impact issues and suggest concrete code-level fixes."
        ),
        "findings": finding_payload,
        "changed_files": changed_payload,
    }

    response = client.responses.create(
        model=settings.openai_model,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(user_prompt)},
        ],
        temperature=0.2,
    )

    return (response.output_text or "No AI summary generated.").strip()
