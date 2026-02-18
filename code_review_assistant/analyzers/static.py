from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

from code_review_assistant.models import Finding


def run_ruff(path: str) -> list[Finding]:
    target = Path(path)
    if not target.exists():
        raise FileNotFoundError(f"Path not found: {path}")

    ruff_bin = shutil.which("ruff")
    cmd = [ruff_bin, "check", str(target), "--output-format", "json"] if ruff_bin else [
        sys.executable,
        "-m",
        "ruff",
        "check",
        str(target),
        "--output-format",
        "json",
    ]
    completed = subprocess.run(cmd, capture_output=True, text=True, check=False)

    if completed.returncode not in (0, 1):
        raise RuntimeError(completed.stderr.strip() or "ruff failed")

    if not completed.stdout.strip():
        return []

    payload = json.loads(completed.stdout)
    findings: list[Finding] = []

    for issue in payload:
        location = issue.get("location") or {}
        findings.append(
            Finding(
                tool="ruff",
                file_path=issue.get("filename", ""),
                line=location.get("row"),
                severity="medium",
                message=issue.get("message", "Style issue"),
                suggestion=(issue.get("fix") or {}).get("message"),
                rule_id=issue.get("code"),
            )
        )

    return findings
