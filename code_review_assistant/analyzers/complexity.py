from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

from code_review_assistant.models import Finding


def run_complexity(path: str, min_grade: str = "C") -> list[Finding]:
    target = Path(path)
    if not target.exists():
        raise FileNotFoundError(f"Path not found: {path}")

    radon_bin = shutil.which("radon")
    cmd = [radon_bin, "cc", "-j", "-s", str(target)] if radon_bin else [
        sys.executable,
        "-m",
        "radon",
        "cc",
        "-j",
        "-s",
        str(target),
    ]
    completed = subprocess.run(cmd, capture_output=True, text=True, check=False)

    if completed.returncode not in (0, 1):
        raise RuntimeError(completed.stderr.strip() or "radon failed")

    if not completed.stdout.strip():
        return []

    data = json.loads(completed.stdout)
    findings: list[Finding] = []

    min_index = ord(min_grade.upper()) - ord("A")

    for file_path, blocks in data.items():
        for block in blocks:
            rank = (block.get("rank") or "A").upper()
            if ord(rank) - ord("A") < min_index:
                continue

            findings.append(
                Finding(
                    tool="radon",
                    file_path=file_path,
                    line=block.get("lineno"),
                    severity="high" if rank in {"E", "F"} else "medium",
                    message=(
                        f"High cyclomatic complexity ({block.get('complexity')}) in "
                        f"{block.get('type', 'block')} `{block.get('name', 'unknown')}`"
                    ),
                    suggestion="Refactor into smaller functions and simplify branching.",
                    rule_id=f"CC-{rank}",
                )
            )

    return findings
