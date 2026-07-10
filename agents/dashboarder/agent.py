"""Dashboarder: un dashboard Malloy es UN query — nest: + tags de render.

Explora el modelo por MCP de Publisher, genera el query, lo valida por
compilación, lo ejecuta con EUC para la vista previa y lo persiste vía PR.
"""
import json
import os

from google.adk.agents import Agent

from shared.euc import UserContext, bq_client_as_user
from shared.git_provider import GitProvider
from shared.publisher_mcp import PublisherMCP

_mcp = PublisherMCP(os.environ["PUBLISHER_MCP_URL"])
_git = GitProvider(repo=os.environ["SEMANTIC_REPO"], token=os.environ["GITHUB_TOKEN"])


def describir_source(package: str, source: str) -> dict:
    """Dimensiones y medidas disponibles en un source del modelo."""
    return _mcp.describe_source(package, source)


def compilar_query(package: str, malloy_query: str) -> str:
    """Malloy -> SQL vía Publisher. El SQL nunca se ejecuta con credenciales de plataforma."""
    return _mcp.compile_query(package, malloy_query)


def ejecutar_preview(sql: str) -> list[dict]:
    """Vista previa con la identidad del usuario (EUC). Máx. 50 filas."""
    ctx = UserContext.from_a2a_headers(_current_headers())
    client = bq_client_as_user(ctx, os.environ["GOOGLE_CLOUD_PROJECT"])
    rows = client.query(sql).result(max_results=50)
    return [dict(r) for r in rows]


def proponer_dashboard(dashboard_spec_json: str, malloy_path: str, malloy_source: str) -> str:
    """Persiste el dashboard vía PR con el DashboardSpec como cuerpo."""
    spec = json.loads(dashboard_spec_json)
    branch = f"dashboarder/{spec['package']}-{spec['name']}"
    return _git.propose(
        branch=branch,
        files={malloy_path: malloy_source},
        spec=spec,
        title=f"[{spec['package']}] dashboard: {spec['name']}",
    )


def _current_headers() -> dict:
    # Inyectado por el middleware A2A en Cloud Run (ver shared/a2a.py)
    return json.loads(os.environ.get("_A2A_HEADERS", "{}"))


root_agent = Agent(
    name="dashboarder",
    model="gemini-2.5-pro",
    instruction=(
        "Construyes dashboards Malloy: un query raíz con vistas anidadas (nest:) "
        "y tags de render (# dashboard, # line_chart, # bar_chart, # table). "
        "Flujo: describir_source -> redactar el query -> compilar_query (si falla, "
        "corrige) -> ejecutar_preview para confirmar con el usuario -> "
        "proponer_dashboard con su DashboardSpec. La preview SIEMPRE corre con la "
        "identidad del usuario; si BQ deniega, explícalo — no escales privilegios."
    ),
    tools=[describir_source, compilar_query, ejecutar_preview, proponer_dashboard],
)
