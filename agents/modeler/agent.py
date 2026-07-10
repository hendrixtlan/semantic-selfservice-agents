"""Modeler: evoluciona el modelo semántico .malloy vía proponer/aprobar/aplicar.

Flujo: contexto del Resolver -> genera SourceSpec + .malloy -> Validator
(compila + dry-run EUC) -> PR con el spec en el cuerpo. Jamás push a main.
"""
import json
import os

import requests
from google.adk.agents import Agent

from shared.git_provider import GitProvider

_git = GitProvider(repo=os.environ["SEMANTIC_REPO"], token=os.environ["GITHUB_TOKEN"])


def validar(malloy_source: str, package: str) -> dict:
    """Delegación al Validator: ¿compila? ¿dry-run OK con la identidad del usuario?"""
    r = requests.post(
        f"{os.environ['VALIDATOR_URL']}/validate",
        json={"malloy": malloy_source, "package": package},
        headers={"Authorization": os.environ.get("_EUC_AUTH", "")},  # propagado por a2a
        timeout=120,
    )
    return r.json()


def proponer_pr(source_spec_json: str, malloy_path: str, malloy_source: str) -> str:
    """Abre el PR con el SourceSpec como cuerpo. Devuelve la URL."""
    spec = json.loads(source_spec_json)
    branch = f"modeler/{spec['package']}-{spec['change_type']}-{spec['source_name']}"
    return _git.propose(
        branch=branch,
        files={malloy_path: malloy_source},
        spec=spec,
        title=f"[{spec['package']}] {spec['change_type']}: {spec['source_name']}",
    )


root_agent = Agent(
    name="modeler",
    model="gemini-2.5-pro",
    instruction=(
        "Generas y modificas sources Malloy (.malloy) del modelo semántico gobernado. "
        "Reglas: (1) catalog-first — solo campos con referencia del Resolver; "
        "(2) todo cambio produce un SourceSpec conforme a docs/contracts/source_spec.schema.json; "
        "(3) antes de abrir PR, valida con la herramienta `validar` — si no compila, corrige; "
        "(4) nunca escribes a main: solo `proponer_pr`. "
        "Estilo Malloy: measures con nombre de negocio, dimensions derivadas "
        "documentadas con comentario, joins con relationship explícita."
    ),
    tools=[validar, proponer_pr],
)
