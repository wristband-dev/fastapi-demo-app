output "config_project_id" {
  description = "The project ID extracted from project_config.yml"
  value       = local.project_id
}

output "project_exists" {
  description = "Whether the project exists in GCP"
  value       = var.check_only ? try(data.google_project.project[0].project_id, "") != "" : true
}

output "project_name" {
  description = "The name of the GCP project"
  value       = var.check_only ? try(data.google_project.project[0].name, local.project_name) : local.project_name
}

output "project_number" {
  description = "The project number"
  value       = var.check_only ? try(data.google_project.project[0].number, "Not available") : try(google_project.project[0].number, "Creating...")
}

output "project_action" {
  description = "The action performed on the project"
  value       = var.check_only ? (try(data.google_project.project[0].project_id, "") != "" ? "Project exists" : "Project doesn't exist") : (try(data.google_project.project[0].project_id, "") != "" ? "Project exists" : "Project created")
}

output "user_has_access" {
  description = "Whether the user has access to the project"
  value       = true # If we get this far, the user has access or the project was created
}

output "firebase_hosting_production" {
  description = "The Firebase Hosting URL for production"
  value       = "https://${local.project_id}.web.app"
}

output "firebase_hosting_staging" {
  description = "The Firebase Hosting URL for staging"
  value       = "https://${local.project_id}-staging.web.app"
} 