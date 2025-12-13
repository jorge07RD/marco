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


  # lifecycle {
  #   prevent_destroy = true
  # }
}

# ═══════════════════════════════════════════════════════
# Repositorio GitHub conectado a Cloud Build
# ═══════════════════════════════════════════════════════


# # ═══════════════════════════════════════════════════════
# # Trigger de Cloud Build
# # ═══════════════════════════════════════════════════════
# resource "google_cloudbuild_trigger" "docker_build" {
#   name        = "build-desde-dockerfile"
#   description = "Construye imagen desde Dockerfile.backend en el repo"
#   location    = "southamerica-east1"
#   project     = var.project

#   # Configuración del repositorio (2nd gen)
#   repository_event_config {
#     repository = google_cloudbuildv2_repository.marco_repo.id

#     push {
#       branch = "^main$"
#     }
#   }

#   # Usar archivo cloudbuild.yaml del repositorio
#   filename = "cloudbuild.yaml"
# }
# projects/niceproyec/locations/southamerica-east1/connections/marco-github-connection/repositories/marco

# resource "google_cloudbuild_trigger" "backend" {
#   name        = "build-desde-dockerfile"
#   description = "Construye imagen desde Dockerfile.backend"
#   location    = "southamerica-east1"
#   project     = var.project

#   repository_event_config {
#     repository = google_cloudbuildv2_repository.marco_repo.id
#     push {
#       branch = "^main$"
#     }
#   }

#   build {
#     step {
#       name = "gcr.io/cloud-builders/docker"
#       args = [
#         "build",
#         "-t", "gcr.io/$PROJECT_ID/mi-app-backend:$COMMIT_SHA",
#         "-t", "gcr.io/$PROJECT_ID/mi-app-backend:latest",
#         "-f", "Dockerfile.backend",
#         "."
#       ]
#     }
#     step {
#       name = "gcr.io/cloud-builders/docker"
#       args = [
#         "push",
#         "--all-tags",
#         "gcr.io/$PROJECT_ID/mi-app-backend"
#       ]
#     }
#     images = [
#       "gcr.io/$PROJECT_ID/mi-app-backend:$COMMIT_SHA",
#       "gcr.io/$PROJECT_ID/mi-app-backend:latest"
#     ]
#     timeout = "1200s"
#   }
# }
# Mostrar la URL del bucket



# resource "google_cloudbuildv2_repository" "marco_repo" {
#   name              = "marco_pro"
#   parent_connection = "projects/${var.project}/locations/${var.region}/connections/marco"
#   remote_uri        = "https://github.com/jorge07RD/marco.git"
#   location          = var.region
# }


# resource "google_cloudbuild_trigger" "backend" {
#   location    = var.region
#   name        = "build-desde-dockerfile"
#   description = "Construye imagen desde Dockerfile.backend en el repo"
#   repository_event_config {
#     repository = google_cloudbuildv2_repository.marco_repo.id
#     push {
#       branch = "^main$"
#     }
#   }
#   filename = "Dockerfile.backend"
# }

output "bucket_url" {
  value = google_storage_bucket.datos.url
}