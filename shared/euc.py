"""EUC (End-User Credentials): la cadena de identidad de la cuadrilla.

Regla no negociable: todo camino de DATOS corre con el token OAuth del
usuario final. Application Default Credentials solo se permiten para
metadatos de plataforma (Dataplex read, GitHub App), nunca para BigQuery
en respuesta a una pregunta del usuario.

El token llega en el header Authorization del request A2A y se propaga
intacto: GE -> orquestador -> especialista -> BigQuery.
"""
from dataclasses import dataclass

from google.cloud import bigquery
from google.oauth2.credentials import Credentials


@dataclass(frozen=True)
class UserContext:
    email: str
    access_token: str

    @classmethod
    def from_a2a_headers(cls, headers: dict) -> "UserContext":
        auth = headers.get("authorization", "")
        if not auth.lower().startswith("bearer "):
            raise PermissionError("EUC roto: request sin token de usuario. No hay fallback a ADC.")
        token = auth.split(" ", 1)[1]
        email = headers.get("x-goog-authenticated-user-email", "desconocido")
        return cls(email=email, access_token=token)


def bq_client_as_user(ctx: UserContext, project: str) -> bigquery.Client:
    """Cliente BQ con la identidad del usuario. RLS/CLS aplican solas."""
    creds = Credentials(token=ctx.access_token)
    return bigquery.Client(project=project, credentials=creds)


def dry_run_as_user(ctx: UserContext, project: str, sql: str) -> int:
    """Dry-run del SQL compilado desde Malloy. Devuelve bytes estimados.

    Es el gate del Validator: si el usuario no puede dry-runear el query,
    tampoco podría verlo en el dashboard — fallamos temprano y con su identidad.
    """
    client = bq_client_as_user(ctx, project)
    job = client.query(sql, job_config=bigquery.QueryJobConfig(dry_run=True, use_query_cache=False))
    return job.total_bytes_processed
