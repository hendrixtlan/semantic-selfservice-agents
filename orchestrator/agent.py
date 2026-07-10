"""Orquestador de semantic-selfservice-agents (Vertex AI Agent Engine).

General 'aburrido a propósito': cero herramientas de dominio. Clasifica,
delega vía RemoteA2aAgent y sintetiza. Nada de tocar BigQuery ni Publisher.
"""
import os

from google.adk.agents import Agent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

resolver = RemoteA2aAgent(
    name="resolver",
    agent_card=f"{os.environ['RESOLVER_URL']}/.well-known/agent-card.json",
)
modeler = RemoteA2aAgent(
    name="modeler",
    agent_card=f"{os.environ['MODELER_URL']}/.well-known/agent-card.json",
)
dashboarder = RemoteA2aAgent(
    name="dashboarder",
    agent_card=f"{os.environ['DASHBOARDER_URL']}/.well-known/agent-card.json",
)
validator = RemoteA2aAgent(
    name="validator",
    agent_card=f"{os.environ['VALIDATOR_URL']}/.well-known/agent-card.json",
)

INSTRUCTION = """Eres el orquestador de la cuadrilla semantic-selfservice-agents
(BI gobernado con Malloy). Tu tabla de routing:

- Descubrimiento / "¿qué significa X?" / "¿qué campos hay?" -> resolver
- Métrica, dimensión o source nuevo en el modelo semántico -> modeler
- Dashboard nuevo o modificado -> dashboarder
- Los especialistas invocan a validator; tú no lo expones al usuario.

Fuera de dominio (predicciones, SQL ad-hoc de larga cola): responde
out_of_domain con la cuadrilla sugerida (ds-lab-agents, bq-adhoc-agents).
Nunca inventes esquemas: si falta contexto de catálogo, pasa por resolver
primero. Propaga siempre el header Authorization (EUC).
"""

root_agent = Agent(
    name="semantic_selfservice_orchestrator",
    model="gemini-2.5-pro",
    instruction=INSTRUCTION,
    sub_agents=[resolver, modeler, dashboarder, validator],
)
