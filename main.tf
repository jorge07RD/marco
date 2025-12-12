terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "6.8.0"
    }
  }
}

provider "google" {
  project = var.project
  region  = var.region
  zone    = var.zone
}

resource "google_compute_network" "vpc_network" {
  name = "terraform-network"
}

# ═══════════════════════════════════════════════════════
# NUEVO: Regla de firewall para permitir SSH
# ═══════════════════════════════════════════════════════
# resource "google_compute_firewall" "allow_ssh" {
#   name    = "terraform-allow-ssh"
#   network = google_compute_network.vpc_network.name

#   allow {
#     protocol = "tcp"
#     ports    = ["22"]
#   }

#   source_ranges = ["0.0.0.0/0"]
#   target_tags   = ["ssh-enabled"]
# }



#   # ═══════════════════════════════════════════════════════
#   # NUEVO: Recurso para crear un bucket de almacenamiento
#   # ═══════════════════════════════════════════════════════

resource "google_storage_bucket" "datos" {
  name          = "${var.project}-datos-bucket" # Usa el project ID para unicidad
  location      = var.region
  storage_class = "STANDARD"

  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"

  soft_delete_policy {
    retention_duration_seconds = 604800
  }


  lifecycle {
    prevent_destroy = true
  }
}

# ═══════════════════════════════════════════════════════
# Repositorio GitHub conectado a Cloud Build
# ═══════════════════════════════════════════════════════
resource "google_cloudbuildv2_repository" "marco_repo" {
  name              = "marco"
  parent_connection = "projects/242884135694/locations/southamerica-east1/connections/marco-github-connection"
  remote_uri        = "https://github.com/jorge07RD/marco.git"
  location          = "southamerica-east1"
  project           = var.project
}

# ═══════════════════════════════════════════════════════
# Trigger de Cloud Build
# ═══════════════════════════════════════════════════════
resource "google_cloudbuild_trigger" "docker_build" {
  name        = "build-desde-dockerfile"
  description = "Construye imagen desde Dockerfile.backend en el repo"
  location    = "southamerica-east1"
  project     = var.project

  # Configuración del repositorio (2nd gen)
  repository_event_config {
    repository = google_cloudbuildv2_repository.marco_repo.id

    push {
      branch = "^main$"
    }
  }

  # Usar archivo cloudbuild.yaml del repositorio
  filename = "cloudbuild.yaml"
}

# Mostrar la URL del bucket
output "bucket_url" {
  value = google_storage_bucket.datos.url
}