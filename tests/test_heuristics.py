from pathlib import Path

from code_review_assistant.analyzers.heuristics import run_bug_risk_heuristics


def test_detects_mutable_default_and_eval(tmp_path: Path) -> None:
    sample = tmp_path / "sample.py"
    sample.write_text(
        """
def unsafe(a=[]):
    eval('1+1')
    try:
        return a
    except:
        return []
""".strip(),
        encoding="utf-8",
    )

    findings = run_bug_risk_heuristics(str(sample))
    rule_ids = {item.rule_id for item in findings}

    assert "HR001" in rule_ids
    assert "HR002" in rule_ids
    assert "HR003" in rule_ids
