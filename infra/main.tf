# Infraestructura mínima de semantic-selfservice-agents.
# Espejo de los repos hermanos: Cloud Run con ingress interno, WIF para CI,
# Artifact Registry, y el orquestador en Vertex AI Agent Engine (deploy por Makefile).

variable "project" { type = string }
variable "region"  { type = string, default = "us-central1" }

locals {
  especialistas = ["resolver", "modeler", "dashboarder", "validator"]
}

resource "google_artifact_registry_repository" "repo" {
  project       = var.project
  location      = var.region
  repository_id = "semantic-selfservice-agents"
  format        = "DOCKER"
}

resource "google_cloud_run_v2_service" "especialista" {
  for_each = toset(local.especialistas)
  project  = var.project
  location = var.region
  name     = "semantic-ssa-${each.key}"
  ingress  = "INGRESS_TRAFFIC_INTERNAL_ONLY"

  template {
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project}/semantic-selfservice-agents/${each.key}:latest"
      env {
        name  = "GOOGLE_CLOUD_PROJECT"
        value = var.project
      }
    }
  }
}

resource "google_cloud_run_v2_service" "publisher" {
  project  = var.project
  location = var.region
  name     = "malloy-publisher"
  ingress  = "INGRESS_TRAFFIC_INTERNAL_ONLY"

  template {
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project}/semantic-selfservice-agents/publisher:latest"
      ports { container_port = 4000 }
    }
  }
}

# WIF para el job "aplicar" del CI — sin llaves exportadas
resource "google_iam_workload_identity_pool" "gh" {
  project                   = var.project
  workload_identity_pool_id = "gh-semantic-ssa"
}

output "publisher_url" { value = google_cloud_run_v2_service.publisher.uri }
output "especialistas" { value = { for k, s in google_cloud_run_v2_service.especialista : k => s.uri } }
