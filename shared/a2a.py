"""Helpers A2A: envoltura mínima para exponer un agente ADK como servicio
A2A en Cloud Run y para el protocolo de rebote entre cuadrillas."""

OUT_OF_DOMAIN = "out_of_domain"
MAX_HOPS = 2


def rebote(sugerencia: str, motivo: str) -> dict:
    """Respuesta estándar cuando la pregunta no es de este dominio.

    El hub re-rutea; el contador de saltos evita loops (máx. 2).
    """
    return {"status": OUT_OF_DOMAIN, "suggested_squad": sugerencia, "reason": motivo}
