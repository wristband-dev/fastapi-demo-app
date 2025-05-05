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

# Check and validate billing account
resource "null_resource" "billing_account_validation" {
  # This will fail fast if billing account is not properly set
  provisioner "local-exec" {
    command = <<EOT
      # Check if billing account is provided
      if [ -z "$GCP_BILLING_ACCOUNT_ID" ] && [ -z "${var.billing_account}" ]; then
        echo "ERROR: No billing account provided."
        echo "========================================================================"
        echo "  BILLING ACCOUNT IS REQUIRED"
        echo "========================================================================"
        echo "You must provide a billing account ID via either:"
        echo "- Environment variable: export GCP_BILLING_ACCOUNT_ID=XXXXX-XXXXX-XXXXX"
        echo "- Or as a Terraform variable: -var=\"billing_account=XXXXX-XXXXX-XXXXX\""
        echo "========================================================================"
        exit 1
      fi
      
      # Use the provided billing account
      BILLING_ACCOUNT=${var.billing_account}
      if [ -z "$BILLING_ACCOUNT" ]; then
        BILLING_ACCOUNT=$GCP_BILLING_ACCOUNT_ID
      fi
      
      echo "Using billing account: $BILLING_ACCOUNT"
      echo $BILLING_ACCOUNT > /tmp/gcp_billing_account_id
    EOT
    interpreter = ["bash", "-c"]
  }
}

# Read the billing account ID from the file
data "local_file" "billing_account_file" {
  filename = "/tmp/gcp_billing_account_id"
  depends_on = [null_resource.billing_account_validation]
}

locals {
  # Get the billing account ID - this will never be empty due to validation above
  billing_account = trimspace(data.local_file.billing_account_file.content)
}

provider "google" {
  project = local.project_id
  region  = var.gcp_region
}

# Check if user has access
resource "null_resource" "check_access" {
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
  lifecycle {
    prevent_destroy = true
  }

  depends_on = [
    null_resource.billing_account_validation,
    null_resource.check_access
  ]
}

# Verify billing is actually enabled and retry if needed
resource "null_resource" "verify_billing" {
  count = var.check_only ? 0 : 1

  provisioner "local-exec" {
    command = <<EOT
      echo "Verifying billing account is enabled for project ${local.project_id}..."
      
      MAX_RETRIES=5
      RETRY_COUNT=0
      SUCCESS=false
      
      while [ $RETRY_COUNT -lt $MAX_RETRIES ] && [ "$SUCCESS" != "true" ]; do
        # First try to link the billing account
        echo "Attempt $((RETRY_COUNT+1)) to link billing account ${local.billing_account} to project ${local.project_id}..."
        gcloud billing projects link ${local.project_id} --billing-account=${local.billing_account} || true
        
        # Wait a moment for propagation
        sleep 10
        
        # Verify billing is enabled
        PROJECT_BILLING=$(gcloud billing projects describe ${local.project_id} --format="value(billingEnabled)" 2>/dev/null || echo "error")
        
        if [ "$PROJECT_BILLING" = "true" ]; then
          echo "✓ Billing successfully enabled for project ${local.project_id}!"
          SUCCESS=true
          break
        else
          echo "! Billing not yet enabled. Retrying in 10 seconds..."
          RETRY_COUNT=$((RETRY_COUNT+1))
          sleep 10
        fi
      done
      
      if [ "$SUCCESS" != "true" ]; then
        echo "ERROR: Could not enable billing for project ${local.project_id} after $MAX_RETRIES attempts."
        echo ""
        echo "========================================================================"
        echo "  BILLING ACCOUNT LINKING FAILED"
        echo "========================================================================"
        echo "Attempted to link ${local.project_id} to billing account ${local.billing_account}"
        echo "but the operation failed. This could be due to:"
        echo ""
        echo "1. The billing account doesn't exist"
        echo "2. You don't have permission to use this billing account"
        echo "3. The billing account is closed or disabled"
        echo "4. GCP API latency issues - try running terraform apply again"
        echo "========================================================================"
        exit 1
      else
        echo "Billing account ${local.billing_account} successfully linked to project ${local.project_id}"
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

# Local to determine the effective project resource
locals {
  effective_project = var.check_only ? (length(data.google_project.project) > 0 ? data.google_project.project[0] : null) : google_project.project[0]
} 