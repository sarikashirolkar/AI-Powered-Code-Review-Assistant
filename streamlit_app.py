from __future__ import annotations

from collections import Counter

import streamlit as st

from code_review_assistant.ai.chatbot import ask_review_bot
from code_review_assistant.config import get_settings
from code_review_assistant.models import ReviewReport
from code_review_assistant.reporting.formatter import to_json, to_markdown
from code_review_assistant.review_engine import review_code_snippet, review_github_pr, review_local_path


st.set_page_config(page_title="AI Code Review Assistant", layout="wide")


def _render_metrics(report: ReviewReport) -> None:
    severities = Counter(item.severity for item in report.findings)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Findings", len(report.findings))
    col2.metric("High", severities.get("high", 0))
    col3.metric("Medium", severities.get("medium", 0))
    col4.metric("Low", severities.get("low", 0))


def _render_report(report: ReviewReport) -> None:
    st.subheader("Review Report")
    _render_metrics(report)

    if report.ai_summary:
        st.markdown("### AI Insights")
        st.markdown(report.ai_summary)

    st.markdown("### Findings")
    if not report.findings:
        st.info("No findings found.")
    else:
        for item in report.findings:
            with st.expander(f"[{item.severity.upper()}] {item.file_path}:{item.line or '-'} - {item.tool}"):
                st.write(item.message)
                if item.suggestion:
                    st.caption(f"Suggestion: {item.suggestion}")
                if item.rule_id:
                    st.caption(f"Rule: {item.rule_id}")

    markdown_report = to_markdown(report)
    json_report = to_json(report)

    c1, c2 = st.columns(2)
    c1.download_button(
        "Download Markdown",
        markdown_report,
        file_name="review_report.md",
        mime="text/markdown",
        use_container_width=True,
    )
    c2.download_button(
        "Download JSON",
        json_report,
        file_name="review_report.json",
        mime="application/json",
        use_container_width=True,
    )


def _chat_section(report: ReviewReport) -> None:
    st.subheader("Review Bot")
    st.caption("Ask questions about this report: prioritization, fixes, refactors, and test strategy.")

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input("Ask the bot about this review...")
    if not question:
        return

    st.session_state.chat_messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    settings = get_settings()
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer = ask_review_bot(settings=settings, report=report, question=question)
        st.markdown(answer)

    st.session_state.chat_messages.append({"role": "assistant", "content": answer})


def _set_latest_report(report: ReviewReport) -> None:
    st.session_state.latest_report = report
    st.session_state.chat_messages = []


def _local_review_tab() -> None:
    st.markdown("### Local Path Review")
    path = st.text_input("Path to file/folder", value=".")
    complexity_threshold = st.selectbox("Complexity threshold", ["A", "B", "C", "D", "E", "F"], index=2)
    use_ai = st.checkbox("Use AI summary", value=True)

    if st.button("Run Local Review", use_container_width=True):
        try:
            report = review_local_path(path=path, complexity_threshold=complexity_threshold, use_ai=use_ai)
            _set_latest_report(report)
            st.success("Review completed.")
        except Exception as exc:
            st.error(f"Review failed: {exc}")


def _pr_review_tab() -> None:
    st.markdown("### GitHub PR Review")
    repo = st.text_input("Repository (owner/name)", value="")
    pr_number = st.number_input("PR number", min_value=1, step=1, value=1)
    use_ai = st.checkbox("Use AI summary for PR", value=True)

    if st.button("Run PR Review", use_container_width=True):
        if not repo:
            st.error("Repository is required.")
            return

        try:
            report = review_github_pr(repo=repo, pr_number=int(pr_number), use_ai=use_ai)
            _set_latest_report(report)
            st.success("PR review completed.")
        except Exception as exc:
            st.error(f"PR review failed: {exc}")


def _snippet_review_tab() -> None:
    st.markdown("### Paste Code Review")
    st.caption("Paste Python code and run instant review without saving files.")
    code = st.text_area(
        "Paste Python code",
        height=260,
        placeholder="def unsafe(data=[]):\n    try:\n        eval('1+1')\n    except:\n        return data",
    )
    complexity_threshold = st.selectbox(
        "Complexity threshold for snippet",
        ["A", "B", "C", "D", "E", "F"],
        index=2,
        key="snippet_complexity_threshold",
    )
    use_ai = st.checkbox("Use AI summary for snippet", value=True, key="snippet_use_ai")

    if st.button("Review Pasted Code", use_container_width=True):
        try:
            report = review_code_snippet(
                code=code,
                filename="snippet.py",
                complexity_threshold=complexity_threshold,
                use_ai=use_ai,
            )
            _set_latest_report(report)
            st.success("Snippet review completed.")
        except Exception as exc:
            st.error(f"Snippet review failed: {exc}")


def main() -> None:
    st.title("AI-Powered Code Review Assistant")
    st.caption("Static analysis + complexity checks + AI-powered review bot")

    local_tab, pr_tab, snippet_tab = st.tabs(["Local Review", "PR Review", "Paste Code"])

    with local_tab:
        _local_review_tab()

    with pr_tab:
        _pr_review_tab()

    with snippet_tab:
        _snippet_review_tab()

    report = st.session_state.get("latest_report")
    if report:
        st.divider()
        _render_report(report)
        st.divider()
        _chat_section(report)
    else:
        st.info("Run a local or PR review to view findings and use the bot.")


if __name__ == "__main__":
    main()
