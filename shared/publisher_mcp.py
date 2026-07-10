"""Cliente del MCP API de Malloy Publisher (:4040).

Los especialistas consultan el modelo semántico por MCP: listar packages,
describir sources y compilar queries a SQL. Publisher NO ejecuta datos en
el camino del usuario — la ejecución la hace el especialista vía euc.py.
"""
import requests


class PublisherMCP:
    def __init__(self, base_url: str):
        self.base = base_url.rstrip("/")

    def _call(self, method: str, params: dict) -> dict:
        r = requests.post(
            f"{self.base}/mcp",
            json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params},
            timeout=30,
        )
        r.raise_for_status()
        payload = r.json()
        if "error" in payload:
            raise RuntimeError(payload["error"])
        return payload["result"]

    def describe_source(self, package: str, source: str) -> dict:
        """Dimensiones y medidas disponibles — el 'explore' del Dashboarder."""
        return self._call("tools/call", {
            "name": "describe_source",
            "arguments": {"package": package, "source": source},
        })

    def compile_query(self, package: str, malloy_query: str) -> str:
        """Compila Malloy -> SQL. El SQL se ejecuta después con EUC."""
        result = self._call("tools/call", {
            "name": "compile_query",
            "arguments": {"package": package, "query": malloy_query},
        })
        return result["sql"]
