# AI-Powered Code Review Assistant

An AI-assisted code review tool that combines static analysis with LLM-based recommendations.

This project automatically reviews code for:
- Code style violations (`ruff`)
- Cyclomatic complexity risks (`radon`)
- Common bug-prone patterns (custom AST heuristics)
- Optional AI suggestions using OpenAI models
- Streamlit-based web UI with an interactive review bot

It also supports GitHub Pull Request review using the GitHub API.

## Why This Project

This repo demonstrates practical integration of:
- Software engineering quality checks
- NLP/LLM-assisted feedback loops
- Dev workflow automation with GitHub and OpenAI APIs

It is designed as a clean, extensible foundation for an interview/portfolio project.

## Tech Stack

- Python 3.10+
- OpenAI API
- Ollama (optional local LLM)
- GitHub REST API
- Ruff
- Radon
- Streamlit
- Pytest

## Project Structure

```text
code_review_assistant/
  analyzers/
    static.py        # style violations via ruff
    complexity.py    # cyclomatic complexity via radon
    heuristics.py    # AST-based potential bug checks
  ai/
    reviewer.py      # AI summary (OpenAI or Ollama)
    chatbot.py       # interactive review bot
    provider.py      # LLM provider routing (auto/openai/ollama)
  github/
    client.py        # GitHub PR file/patch fetch
  reporting/
    formatter.py     # markdown/json report rendering
  cli.py             # main CLI entrypoint
  review_engine.py   # reusable orchestration for CLI/UI
streamlit_app.py     # web interface
tests/
  test_heuristics.py
```

## Quick Start

### 1) Clone and install

```bash
git clone https://github.com/sarikashirolkar/AI-Powered-Code-Review-Assistant.git
cd AI-Powered-Code-Review-Assistant
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 2) Configure environment

```bash
cp .env.example .env
```

Set values in `.env`:
- `LLM_PROVIDER`: `auto` (default), `openai`, or `ollama`
- `OPENAI_API_KEY`: required only when using OpenAI
- `OPENAI_MODEL`: optional, defaults to `gpt-4o-mini`
- `OLLAMA_HOST`: optional, defaults to `http://localhost:11434`
- `OLLAMA_MODEL`: optional, defaults to `llama3.1:8b`
- `GITHUB_TOKEN`: required for private repos or higher API limits

For local AI without API keys (Ollama):

```bash
ollama serve
ollama pull llama3.1:8b
```

### 3) Run local path review

```bash
code-review-assistant review-path --path . --use-ai --format markdown --output reports/local_review.md
```

Without AI:

```bash
code-review-assistant review-path --path src --format json --output reports/local_review.json
```

### 4) Run GitHub PR review

```bash
code-review-assistant review-pr --repo owner/repo --pr-number 123 --use-ai --format markdown --output reports/pr_123_review.md
```

### 5) Launch Streamlit frontend

```bash
streamlit run streamlit_app.py
```

The frontend includes:
- Local path review
- GitHub PR review
- Paste-code instant review (no file required)
- Download buttons for Markdown/JSON reports
- Chat-style review bot grounded on the generated report

## CLI Reference

### `review-path`

```bash
code-review-assistant review-path \
  --path . \
  --complexity-threshold C \
  --use-ai \
  --format markdown \
  --output reports/review.md
```

Options:
- `--path`: target file or folder (default: `.`)
- `--complexity-threshold`: complexity rank threshold `A-F` (default: `C`)
- `--use-ai`: include OpenAI-generated review summary
- `--format`: `markdown` or `json`
- `--output`: optional output file path

### `review-pr`

```bash
code-review-assistant review-pr \
  --repo owner/repo \
  --pr-number 42 \
  --use-ai \
  --format markdown
```

Options:
- `--repo`: GitHub repo in `owner/name`
- `--pr-number`: PR number
- `--use-ai`: ask OpenAI to review patch metadata/content
- `--format`: `markdown` or `json`
- `--output`: optional output file path

## Example Output (Markdown)

```md
# Code Review Report: /path/to/project

## Summary
- Total findings: 8
- High: 2
- Medium: 5
- Low: 1

## AI Insights
- Refactor the `process_request` function into smaller units to reduce branching.
- Replace bare `except` with explicit exception handling.

## Findings
- [HIGH] `app/service.py:88` `heuristic`: Bare `except:` can hide unexpected failures.
```

## Heuristic Rules Included

- `HR001`: Bare `except`
- `HR002`: `eval`/`exec` usage
- `HR003`: Mutable default arguments
- `HR000`: Python syntax errors in scanned files

## Testing

```bash
pip install -e .[dev]
pytest -q
```

## Future Enhancements

- Inline PR comments via GitHub Checks API
- Security scanners (Bandit/Semgrep) integration
- Embedding-based retrieval for larger codebases
- Team-specific policy engine (custom lint/fix rules)
- Web dashboard for trend tracking over time

## License

MIT
