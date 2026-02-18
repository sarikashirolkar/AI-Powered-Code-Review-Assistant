from __future__ import annotations

import requests


class GitHubClient:
    def __init__(self, token: str | None = None) -> None:
        self.token = token

    def _headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def fetch_pr_files(self, repo: str, pr_number: int) -> list[dict]:
        url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files"
        resp = requests.get(url, headers=self._headers(), timeout=30)
        resp.raise_for_status()

        files = resp.json()
        return [
            {
                "filename": item.get("filename"),
                "status": item.get("status"),
                "additions": item.get("additions"),
                "deletions": item.get("deletions"),
                "changes": item.get("changes"),
                "patch": item.get("patch", "")[:8000],
            }
            for item in files
        ]
