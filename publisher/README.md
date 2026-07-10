# Publisher

Malloy Publisher sirve el modelo de `semantic/` por REST (`:4000`) y MCP (`:4040`).

**Regla EUC**: la conexión BigQuery de `publisher.config.json` usa una service
account de **solo lectura acotada** y existe únicamente para la UI de exploración
de stewards. El camino de datos del usuario final NO pasa por aquí: los
especialistas compilan vía MCP y ejecutan el SQL en BQ con el token del usuario.
