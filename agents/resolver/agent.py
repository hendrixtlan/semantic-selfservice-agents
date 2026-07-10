"""Resolver: catalog-first. Términos de negocio -> activos de Dataplex.

No genera Malloy ni SQL. Su salida (entry_id, fqn, columnas, descripciones)
es el insumo obligatorio del Modeler y el Dashboarder: sin referencia de
catálogo no hay cambio al modelo.
"""
import os

from google.adk.agents import Agent

from shared.catalog_client import CatalogClient

_catalog = CatalogClient(project=os.environ["GOOGLE_CLOUD_PROJECT"])


def buscar_en_catalogo(termino: str) -> list[dict]:
    """Busca un término de negocio en Dataplex y devuelve activos candidatos."""
    return _catalog.search(termino)


def esquema_de_tabla(entry_id: str) -> dict:
    """Esquema autoritativo de una entrada del catálogo."""
    return _catalog.get_schema(entry_id)


root_agent = Agent(
    name="resolver",
    model="gemini-2.5-flash",
    instruction=(
        "Resuelves términos de negocio contra el catálogo Dataplex. "
        "NUNCA respondas de memoria sobre tablas o columnas: usa las herramientas. "
        "Devuelve entry_id + fqn + columnas relevantes; si hay ambigüedad, "
        "presenta los candidatos y pide precisión."
    ),
    tools=[buscar_en_catalogo, esquema_de_tabla],
)
