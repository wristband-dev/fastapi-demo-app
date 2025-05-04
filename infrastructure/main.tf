terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

# Read project_config.yml to get the project ID
data "local_file" "project_config" {
  filename = "${path.module}/../project_config.yml"
}

locals {
  # Extract project ID from project_config.yml using regex
  project_id = replace(
    regex("id: \"([^\"]+)\"", data.local_file.project_config.content)[0],
    "id: \"", ""
  )
  # Extract project name from project_config.yml
  project_name = replace(
    regex("label: \"([^\"]+)\"", data.local_file.project_config.content)[0],
    "label: \"", ""
  )
  # Extract GitHub user from project_config.yml
  github_user = replace(
    regex("github:\\s+user: \"([^\"]+)\"", data.local_file.project_config.content)[0],
    "github:\n    user: \"", ""
  )
  # Extract GitHub repo from project_config.yml
  github_repo = replace(
    regex("repo: \"([^\"]+)\"", data.local_file.project_config.content)[0],
    "repo: \"", ""
  )
}

# Check for billing account ID environment variable
resource "null_resource" "billing_account_check" {
  provisioner "local-exec" {
    command = <<EOT
      echo ""
      echo "Checking for GCP billing account..."
      if [ -n "$GCP_BILLING_ACCOUNT_ID" ]; then
        echo "$GCP_BILLING_ACCOUNT_ID" > /tmp/gcp_billing_account_id
        echo "Found billing account from environment variable: $GCP_BILLING_ACCOUNT_ID"
        echo "BILLING_ACCOUNT_FOUND=true" > /tmp/billing_status
      else
        echo "WARNING: GCP_BILLING_ACCOUNT_ID environment variable is not set."
        echo "MANUAL_SETUP_REQUIRED" > /tmp/gcp_billing_account_id
        echo "BILLING_ACCOUNT_FOUND=false" > /tmp/billing_status
        
        echo ""
        echo "========================================================================"
        echo "  IMPORTANT: Manual billing account setup will be required"
        echo "========================================================================"
        echo "No billing account was provided. You need to manually link a billing account"
        echo "in the GCP Console before proceeding with Terraform apply:"
        echo ""
        echo "1. Go to: https://console.cloud.google.com/billing/linkedaccount?project=${local.project_id}"
        echo "2. Link an existing billing account or create a new one"
        echo "3. Then run 'terraform apply' again to continue setup"
        echo ""
        echo "Alternatively, set the GCP_BILLING_ACCOUNT_ID environment variable:"
        echo "export GCP_BILLING_ACCOUNT_ID=XXXXXX-XXXXXX-XXXXXX"
        echo "========================================================================"
        exit 1  # Stop execution if billing account is not set
      fi
    EOT
    interpreter = ["bash", "-c"]
  }
}

# Read the billing account ID from the file
data "local_file" "billing_account_file" {
  filename = "/tmp/gcp_billing_account_id"
  depends_on = [null_resource.billing_account_check]
}

locals {
  # Process the billing account - either from var, env var, or empty if manual setup is needed
  billing_account_raw = trimspace(data.local_file.billing_account_file.content)
  billing_account = (var.billing_account != "" ? 
                     var.billing_account : 
                     (local.billing_account_raw != "MANUAL_SETUP_REQUIRED" ? 
                       local.billing_account_raw : 
                       ""))
}

provider "google" {
  project = local.project_id
  region  = var.gcp_region
}

# Check if user has access at the organizational level
data "google_client_config" "current" {}

# Try to get project if it exists
data "google_project" "project" {
  count      = var.check_only ? 1 : 0
  project_id = local.project_id
}

# Create project if it doesn't exist
resource "google_project" "project" {
  count           = var.check_only ? 0 : 1
  name            = local.project_name
  project_id      = local.project_id
  org_id          = var.org_id
  billing_account = local.billing_account

  # Only create if project doesn't already exist
  # We rely on Terraform's error handling if the project already exists but user doesn't have access
  lifecycle {
    # Prevent destruction of the project
    prevent_destroy = true
  }

  depends_on = [
    null_resource.billing_account_check
  ]
}

# Check billing account status
resource "null_resource" "verify_billing" {
  count = var.check_only ? 0 : 1

  provisioner "local-exec" {
    command = <<EOT
      echo "Verifying billing account status for project ${local.project_id}..."
      PROJECT_BILLING=$(gcloud billing projects describe ${local.project_id} --format="value(billingEnabled)" 2>/dev/null || echo "error")
      
      if [ "$PROJECT_BILLING" = "error" ] || [ "$PROJECT_BILLING" = "false" ]; then
        echo "ERROR: Project ${local.project_id} does not have billing enabled."
        echo ""
        echo "========================================================================"
        echo "  IMPORTANT: Manual billing account setup is required"
        echo "========================================================================"
        echo "Please enable billing for this project before continuing:"
        echo ""
        echo "1. Go to: https://console.cloud.google.com/billing/linkedaccount?project=${local.project_id}"
        echo "2. Link an existing billing account or create a new one"
        echo "3. Then run 'terraform apply' again to continue setup"
        echo "========================================================================"
        exit 1
      else
        echo "Billing is properly configured for the project."
      fi
    EOT
    interpreter = ["bash", "-c"]
  }

  depends_on = [
    google_project.project
  ]
}

# Enable required APIs
resource "google_project_service" "apis" {
  for_each = toset([
    "cloudresourcemanager.googleapis.com",
    "serviceusage.googleapis.com",
    "run.googleapis.com",
    "containerregistry.googleapis.com",
    "cloudbuild.googleapis.com",
    "firebase.googleapis.com",
    "firestore.googleapis.com",
    "appengine.googleapis.com",
    "artifactregistry.googleapis.com",
    "iam.googleapis.com",
    "cloudscheduler.googleapis.com"
  ])

  project = local.project_id
  service = each.key

  disable_dependent_services = false
  disable_on_destroy         = false

  depends_on = [
    google_project.project,
    null_resource.verify_billing
  ]
}

# Display post-apply instructions if manual billing setup was required
resource "null_resource" "post_apply_instructions" {
  provisioner "local-exec" {
    command = <<EOT
      if [ -f "/tmp/billing_status" ] && grep -q "BILLING_ACCOUNT_FOUND=false" /tmp/billing_status; then
        echo ""
        echo "========================================================================"
        echo "  REMINDER: Manual billing account setup is required"
        echo "========================================================================"
        echo "No billing account was provided during setup. You need to manually link"
        echo "a billing account in the GCP Console before proceeding:"
        echo ""
        echo "1. Go to: https://console.cloud.google.com/billing/linkedaccount?project=${local.project_id}"
        echo "2. Link an existing billing account or create a new one"
        echo "3. Then run 'terraform apply' again to continue setup"
        echo "========================================================================"
      fi
    EOT
    interpreter = ["bash", "-c"]
  }

  depends_on = [
    google_project.project
  ]
}

# Use a local-exec provisioner to check if user has access
resource "null_resource" "check_access" {
  # This will run regardless of whether the project exists or is being created
  provisioner "local-exec" {
    command = <<EOT
      PROJECT_EXISTS=$(gcloud projects describe ${local.project_id} --format=json 2>/dev/null || echo "not_found")
      if [ "$PROJECT_EXISTS" != "not_found" ]; then
        # Project exists, check if user has access
        gcloud projects get-iam-policy ${local.project_id} --format=json 2>/dev/null || {
          echo "ERROR: Project ${local.project_id} exists but you don't have access to it"
          exit 1
        }
        echo "Project exists and user has access"
      else
        echo "Project doesn't exist and will be created"
      fi
    EOT
    interpreter = ["bash", "-c"]
  }
}

# Local to determine the effective project resource
locals {
  effective_project = var.check_only ? (length(data.google_project.project) > 0 ? data.google_project.project[0] : null) : google_project.project[0]
} 