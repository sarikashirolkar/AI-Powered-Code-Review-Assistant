from __future__ import annotations

import json

from code_review_assistant.ai.provider import generate_llm_response
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

    return generate_llm_response(
        settings=settings,
        system_prompt=SYSTEM_PROMPT,
        user_prompt=json.dumps(user_prompt),
    )
