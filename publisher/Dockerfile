# Malloy Publisher para Cloud Run — ingress interno.
# Sirve el modelo semántico versionado en este repo (semantic/).
FROM node:22-slim
WORKDIR /publisher
COPY ../semantic ./semantic
RUN npm install -g @malloy-publisher/server
EXPOSE 4000 4040
# 4000 REST + UI de exploración (stewards) · 4040 MCP (agentes)
CMD ["malloy-publisher-server", "--port", "4000", "--server_root", "semantic/"]
