from __future__ import annotations

import ast
from pathlib import Path

from code_review_assistant.models import Finding


class BugRiskVisitor(ast.NodeVisitor):
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.findings: list[Finding] = []

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        if node.type is None:
            self.findings.append(
                Finding(
                    tool="heuristic",
                    file_path=self.file_path,
                    line=node.lineno,
                    severity="high",
                    message="Bare `except:` can hide unexpected failures.",
                    suggestion="Catch specific exceptions and log meaningful context.",
                    rule_id="HR001",
                )
            )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec"}:
            self.findings.append(
                Finding(
                    tool="heuristic",
                    file_path=self.file_path,
                    line=node.lineno,
                    severity="high",
                    message=f"Use of `{node.func.id}` may introduce security risks.",
                    suggestion="Prefer safer parsing/execution alternatives.",
                    rule_id="HR002",
                )
            )
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        defaults = node.args.defaults or []
        for default in defaults:
            if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                self.findings.append(
                    Finding(
                        tool="heuristic",
                        file_path=self.file_path,
                        line=node.lineno,
                        severity="medium",
                        message=(
                            f"Mutable default argument in function `{node.name}` can cause shared state bugs."
                        ),
                        suggestion="Use `None` as default and instantiate inside the function.",
                        rule_id="HR003",
                    )
                )
        self.generic_visit(node)


def _python_files(path: str) -> list[Path]:
    target = Path(path)
    if target.is_file() and target.suffix == ".py":
        return [target]
    if target.is_dir():
        return [p for p in target.rglob("*.py") if ".venv" not in p.parts and "__pycache__" not in p.parts]
    return []


def run_bug_risk_heuristics(path: str) -> list[Finding]:
    findings: list[Finding] = []
    for py_file in _python_files(path):
        source = py_file.read_text(encoding="utf-8")
        try:
            tree = ast.parse(source)
        except SyntaxError as exc:
            findings.append(
                Finding(
                    tool="heuristic",
                    file_path=str(py_file),
                    line=exc.lineno,
                    severity="high",
                    message=f"Syntax error: {exc.msg}",
                    suggestion="Fix syntax before running deeper analysis.",
                    rule_id="HR000",
                )
            )
            continue

        visitor = BugRiskVisitor(str(py_file))
        visitor.visit(tree)
        findings.extend(visitor.findings)

    return findings
