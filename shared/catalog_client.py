"""catalog-first sobre Dataplex: el LLM nunca recuerda esquemas, los consulta.

Copiado/compartido con bi-selfservice-agents y ds-lab-agents — candidato a
extraerse a la librería común del ecosistema.
"""
from google.cloud import dataplex_v1


class CatalogClient:
    def __init__(self, project: str, location: str = "us"):
        self._client = dataplex_v1.CatalogServiceClient()
        self._scope = f"projects/{project}/locations/{location}"

    def search(self, business_term: str, limit: int = 10) -> list[dict]:
        """Resuelve un término de negocio a entradas del catálogo."""
        request = dataplex_v1.SearchEntriesRequest(
            name=self._scope, query=business_term, page_size=limit
        )
        results = self._client.search_entries(request=request)
        return [
            {
                "entry_id": r.dataplex_entry.name,
                "fqn": r.dataplex_entry.fully_qualified_name,
                "description": r.dataplex_entry.entry_source.description,
            }
            for r in results
        ]

    def get_schema(self, entry_id: str) -> dict:
        """Esquema autoritativo de una tabla. Insumo obligatorio del Modeler."""
        entry = self._client.get_entry(
            request=dataplex_v1.GetEntryRequest(
                name=entry_id, view=dataplex_v1.EntryView.ALL
            )
        )
        aspects = {k: v for k, v in entry.aspects.items() if "schema" in k}
        return {"fqn": entry.fully_qualified_name, "schema_aspects": aspects}
