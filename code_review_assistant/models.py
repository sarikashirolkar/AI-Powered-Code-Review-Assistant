from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class Finding:
    tool: str
    file_path: str
    line: int | None
    severity: str
    message: str
    suggestion: str | None = None
    rule_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ReviewReport:
    target: str
    findings: list[Finding] = field(default_factory=list)
    ai_summary: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_findings(self, new_findings: list[Finding]) -> None:
        self.findings.extend(new_findings)

    def to_dict(self) -> dict[str, Any]:
        return {
            "target": self.target,
            "total_findings": len(self.findings),
            "findings": [item.to_dict() for item in self.findings],
            "ai_summary": self.ai_summary,
            "metadata": self.metadata,
        }
