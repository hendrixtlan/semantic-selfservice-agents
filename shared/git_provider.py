"""Proponer / aprobar / aplicar sobre GitHub.

Los agentes NUNCA hacen push a main. Solo:
  1. branch efímero
  2. commit del .malloy + spec
  3. PR con el spec (SourceSpec/DashboardSpec) como cuerpo
El steward aprueba; el CI compila y aplica (redeploy de Publisher).
"""
import json

import requests

API = "https://api.github.com"


class GitProvider:
    def __init__(self, repo: str, token: str):
        self.repo = repo
        self.headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}

    def propose(self, branch: str, files: dict[str, str], spec: dict, title: str) -> str:
        """Crea branch, commitea archivos y abre PR. Devuelve la URL del PR."""
        base = requests.get(f"{API}/repos/{self.repo}/git/ref/heads/main", headers=self.headers).json()
        requests.post(
            f"{API}/repos/{self.repo}/git/refs", headers=self.headers,
            json={"ref": f"refs/heads/{branch}", "sha": base["object"]["sha"]},
        )
        for path, content in files.items():
            requests.put(
                f"{API}/repos/{self.repo}/contents/{path}", headers=self.headers,
                json={
                    "message": f"propose: {title}",
                    "content": _b64(content),
                    "branch": branch,
                },
            )
        body = f"## Spec\n```json\n{json.dumps(spec, indent=2, ensure_ascii=False)}\n```"
        pr = requests.post(
            f"{API}/repos/{self.repo}/pulls", headers=self.headers,
            json={"title": title, "head": branch, "base": "main", "body": body},
        ).json()
        return pr["html_url"]


def _b64(s: str) -> str:
    import base64
    return base64.b64encode(s.encode()).decode()
