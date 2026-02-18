from __future__ import annotations

from openai import OpenAI

from code_review_assistant.config import Settings


def _openai_chat(settings: Settings, system_prompt: str, user_prompt: str) -> str:
    client = OpenAI(api_key=settings.openai_api_key)
    response = client.responses.create(
        model=settings.openai_model,
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )
    return (response.output_text or "No response generated.").strip()


def _ollama_chat(settings: Settings, system_prompt: str, user_prompt: str) -> str:
    try:
        from ollama import Client
    except ImportError:
        return (
            "Ollama fallback unavailable. Install it with `pip install ollama` and run "
            "`ollama serve`, then pull a model like `ollama pull llama3.1:8b`."
        )

    client = Client(host=settings.ollama_host)
    try:
        response = client.chat(
            model=settings.ollama_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            options={"temperature": 0.2},
        )
    except Exception as exc:
        return (
            "Ollama request failed. Make sure the Ollama server is running (`ollama serve`) "
            f"and model `{settings.ollama_model}` is pulled. Error: {exc}"
        )

    return (response.get("message", {}) or {}).get("content", "No response generated.").strip()


def generate_llm_response(settings: Settings, system_prompt: str, user_prompt: str) -> str:
    provider = (settings.llm_provider or "auto").lower()

    if provider == "openai":
        if not settings.openai_api_key:
            return "LLM_PROVIDER=openai selected but OPENAI_API_KEY is not configured."
        return _openai_chat(settings, system_prompt, user_prompt)

    if provider == "ollama":
        return _ollama_chat(settings, system_prompt, user_prompt)

    if settings.openai_api_key:
        return _openai_chat(settings, system_prompt, user_prompt)

    return _ollama_chat(settings, system_prompt, user_prompt)
