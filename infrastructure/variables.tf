variable "gcp_region" {
  description = "The GCP region to use"
  type        = string
  default     = "us-central1"
}

variable "gcp_zone" {
  description = "The GCP zone to use"
  type        = string
  default     = "us-central1-a"
}

variable "check_only" {
  description = "If true, only check if the project exists and if the user has access. If false, create the project if it doesn't exist."
  type        = bool
  default     = false
}

variable "org_id" {
  description = "The organization ID to create the project under. Required if creating a new project."
  type        = string
  default     = ""
}

variable "billing_account" {
  description = "The billing account to associate with the project. Required if not provided via GCP_BILLING_ACCOUNT_ID env var."
  type        = string
  default     = ""
}

variable "environment" {
  description = "The environment to deploy to (e.g., 'staging', 'production')"
  type        = string
  default     = "staging"
}

variable "trigger_branch" {
  description = "The branch that triggers the deployment"
  type        = string
  default     = "main"  # For staging; use 'main' or 'master' for production
}

variable "firestore_location" {
  description = "The location for the Firestore database (Note: currently hardcoded to 'us-central1')"
  type        = string
  default     = "us-central1"  # Must be a valid Firestore location
}

variable "github_owner" {
  description = "The GitHub username or organization that owns the repository (read from project_config.yml)"
  type        = string
  default     = ""  # Will be overridden by local.github_user
}

variable "github_repo" {
  description = "The name of the GitHub repository (read from project_config.yml)"
  type        = string
  default     = ""  # Will be overridden by local.github_repo
}

variable "image" {
  description = "The Docker image to deploy (if empty, will build from source)"
  type        = string
  default     = ""
} 