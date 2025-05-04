# Cloud Run service to host the FastAPI application
resource "google_cloud_run_service" "fastapi_service" {
  name     = "${local.project_id}-${var.environment}"
  location = var.gcp_region
  project  = local.project_id

  template {
    spec {
      containers {
        image = var.image != "" ? var.image : "gcr.io/${local.project_id}/${local.project_id}-api:latest"
        
        resources {
          limits = {
            cpu    = "1000m"
            memory = "512Mi"
          }
        }
        
        # Environment variables
        env {
          name  = "ENV"
          value = var.environment
        }
        
        env {
          name  = "FIRESTORE_PROJECT_ID"
          value = local.project_id
        }
        
        env {
          name  = "FIRESTORE_COLLECTION_PREFIX"
          value = var.environment
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  # Depends on the Firestore database being created first
  depends_on = [
    google_firestore_database.database
  ]
}

# Make the Cloud Run service publicly accessible
resource "google_cloud_run_service_iam_member" "public_access" {
  service  = google_cloud_run_service.fastapi_service.name
  location = google_cloud_run_service.fastapi_service.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Output the Cloud Run URL
output "fastapi_url" {
  value = google_cloud_run_service.fastapi_service.status[0].url
  description = "The URL of the deployed FastAPI service"
} 