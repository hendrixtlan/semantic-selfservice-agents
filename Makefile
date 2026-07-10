PROJECT ?= $(shell gcloud config get-value project)
REGION  ?= us-central1
REPO    := $(REGION)-docker.pkg.dev/$(PROJECT)/semantic-selfservice-agents

.PHONY: gate publisher-local deploy-agents deploy-publisher deploy-orchestrator

gate:            ## Compile gate local (idéntico al CI)
	node scripts/compile_gate.mjs semantic/packages

publisher-local: ## Publisher en localhost:4000 para desarrollo
	npx @malloy-publisher/server --port 4000 --server_root semantic/

deploy-agents:   ## Build + deploy de los 4 especialistas (ingress interno)
	for a in resolver modeler dashboarder validator; do \
	  gcloud builds submit agents/$$a --tag $(REPO)/$$a:latest && \
	  gcloud run deploy semantic-ssa-$$a --image $(REPO)/$$a:latest \
	    --region $(REGION) --ingress internal --no-allow-unauthenticated; \
	done

deploy-publisher:
	gcloud builds submit publisher --tag $(REPO)/publisher:latest
	gcloud run deploy malloy-publisher --image $(REPO)/publisher:latest \
	  --region $(REGION) --ingress internal --no-allow-unauthenticated

deploy-orchestrator: ## Orquestador a Vertex AI Agent Engine
	cd orchestrator && python -c "from deploy import main; main()"
