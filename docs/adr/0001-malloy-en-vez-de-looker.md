# ADR 0001 — Malloy en vez de Looker como capa semántica

**Estado**: aceptado · **Fecha**: 2026-07

## Contexto
`bi-selfservice-agents` cubre el slot de BI gobernado con Looker: modelo LookML
sincronizado con una instancia, dashboards vía API, entrega por embed SSO. El
patrón proponer/aprobar/aplicar exigía mantener coherencia entre el repo LookML
y el estado de la instancia, y la cadena EUC terminaba en el embed SSO.

## Decisión
Reemplazar Looker por Malloy + Malloy Publisher:
- El modelo semántico son archivos `.malloy` en Git — **el repo es la fuente de
  verdad completa**, sin estado externo que sincronizar.
- Un dashboard es **un query** (nest: + tags de render): un artefacto de texto
  validable por compilación, no una secuencia de llamadas API.
- Publisher expone el modelo por REST y **MCP** — interfaz nativa para agentes.
- El gate de calidad se vuelve **determinístico**: compilar en CI no requiere
  instancia viva ni credenciales de plataforma.
- La cadena EUC se acorta un eslabón: SQL compilado -> BigQuery con el token
  del usuario. RLS/CLS de BQ aplican solas.

## Consecuencias
Positivas: gobierno más simple, CI determinístico, MCP nativo, cero licencias.
Negativas (asumidas): perdemos scheduling/alertas, permisos de contenido por
carpeta y caching/PDTs de Looker. Mitigación en roadmap: Cloud Scheduler +
`DashboardSpec.alerts[]`; BI Engine + tablas materializadas vía PR.
Riesgo: Publisher/Composer son proyectos jóvenes — pineamos versiones y el
compile gate nos avisa de breaking changes al actualizar.
