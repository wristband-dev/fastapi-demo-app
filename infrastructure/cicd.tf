# Cloud Build repository trigger
resource "google_cloudbuild_trigger" "fastapi_deploy" {
  name        = "${local.project_id}-${var.environment}-api"
  description = "Deploy FastAPI to Cloud Run on push to ${var.trigger_branch} branch"
  project     = local.project_id
  
  # Only create if we're not in check-only mode
  count = var.check_only ? 0 : 1

  # GitHub configuration - uses values from project_config.yml
  github {
    owner = coalesce(var.github_owner, local.github_user)
    name  = coalesce(var.github_repo, local.github_repo)
    push {
      branch = var.trigger_branch
    }
  }

  # Include/exclude specific file paths
  included_files = [
    "backend/**",
    "project_config.yml"
  ]

  # Build configuration
  build {
    # Step 1: Build the Docker image
    step {
      name = "gcr.io/cloud-builders/docker"
      args = [
        "build", 
        "-t", "gcr.io/${local.project_id}/${local.project_id}-api:$COMMIT_SHA",
        "-t", "gcr.io/${local.project_id}/${local.project_id}-api:latest",
        "-f", "backend/Dockerfile",
        "./backend"
      ]
    }

    # Step 2: Push the Docker image to Container Registry
    step {
      name = "gcr.io/cloud-builders/docker"
      args = ["push", "gcr.io/${local.project_id}/${local.project_id}-api:$COMMIT_SHA"]
    }

    # Step 3: Deploy to Cloud Run
    step {
      name = "gcr.io/google.com/cloudsdktool/cloud-sdk"
      entrypoint = "gcloud"
      args = [
        "run", "deploy", "${local.project_id}-${var.environment}",
        "--image", "gcr.io/${local.project_id}/${local.project_id}-api:$COMMIT_SHA",
        "--region", var.gcp_region,
        "--platform", "managed",
        "--allow-unauthenticated",
        "--set-env-vars", "ENV=${var.environment},FIRESTORE_PROJECT_ID=${local.project_id},FIRESTORE_COLLECTION_PREFIX=${var.environment}"
      ]
    }

    # Artifacts configuration
    artifacts {
      images = ["gcr.io/${local.project_id}/${local.project_id}-api:$COMMIT_SHA"]
    }
  }

  depends_on = [
    google_project_service.apis
  ]
}

# Manual trigger for FastAPI deployment
resource "google_cloudbuild_trigger" "fastapi_manual" {
  name        = "${local.project_id}-${var.environment}-api-manual"
  description = "Manual trigger to deploy FastAPI to Cloud Run"
  project     = local.project_id
  
  # Only create if we're not in check-only mode
  count = var.check_only ? 0 : 1

  # GitHub configuration
  github {
    owner = coalesce(var.github_owner, local.github_user)
    name  = coalesce(var.github_repo, local.github_repo)
    
    # Manual trigger
    pull_request {
      branch = var.trigger_branch
      comment_control = "COMMENTS_ENABLED"
    }
  }

  # Include/exclude specific file paths
  included_files = [
    "backend/**",
    "project_config.yml"
  ]

  # Build configuration - similar to the automatic trigger
  build {
    step {
      name = "gcr.io/cloud-builders/docker"
      args = [
        "build", 
        "-t", "gcr.io/${local.project_id}/${local.project_id}-api:$COMMIT_SHA",
        "-t", "gcr.io/${local.project_id}/${local.project_id}-api:latest",
        "-f", "backend/Dockerfile",
        "./backend"
      ]
    }

    step {
      name = "gcr.io/cloud-builders/docker"
      args = ["push", "gcr.io/${local.project_id}/${local.project_id}-api:$COMMIT_SHA"]
    }

    step {
      name = "gcr.io/google.com/cloudsdktool/cloud-sdk"
      entrypoint = "gcloud"
      args = [
        "run", "deploy", "${local.project_id}-${var.environment}",
        "--image", "gcr.io/${local.project_id}/${local.project_id}-api:$COMMIT_SHA",
        "--region", var.gcp_region,
        "--platform", "managed",
        "--allow-unauthenticated",
        "--set-env-vars", "ENV=${var.environment},FIRESTORE_PROJECT_ID=${local.project_id},FIRESTORE_COLLECTION_PREFIX=${var.environment}"
      ]
    }

    artifacts {
      images = ["gcr.io/${local.project_id}/${local.project_id}-api:$COMMIT_SHA"]
    }
  }

  depends_on = [
    google_project_service.apis
  ]
}

# Frontend deployment trigger
resource "google_cloudbuild_trigger" "frontend_deploy" {
  name        = "${local.project_id}-${var.environment}-frontend"
  description = "Deploy frontend on push to ${var.trigger_branch} branch"
  project     = local.project_id
  
  # Only create if we're not in check-only mode
  count = var.check_only ? 0 : 1

  # GitHub configuration
  github {
    owner = coalesce(var.github_owner, local.github_user)
    name  = coalesce(var.github_repo, local.github_repo)
    push {
      branch = var.trigger_branch
    }
  }

  # Include/exclude specific file paths
  included_files = [
    "frontend/**",
    "project_config.yml"
  ]

  # Build configuration
  build {
    # Step 1: Install dependencies
    step {
      name = "node:16"
      dir  = "frontend"
      entrypoint = "npm"
      args = ["install"]
    }

    # Step 2: Get the Cloud Run URL
    step {
      name = "gcr.io/google.com/cloudsdktool/cloud-sdk"
      entrypoint = "bash"
      args = [
        "-c",
        "gcloud run services describe ${local.project_id}-${var.environment} --region=${var.gcp_region} --format='value(status.url)' > /workspace/api_url.txt"
      ]
    }

    # Step 3: Build the frontend with the actual Cloud Run URL
    step {
      name = "node:16"
      dir  = "frontend"
      entrypoint = "bash"
      args = [
        "-c",
        "API_URL=$(cat /workspace/api_url.txt) && npm run build -- --env=NEXT_PUBLIC_API_URL=$API_URL --env=NEXT_PUBLIC_ENV=${var.environment}"
      ]
    }

    # Step 4: Deploy to Firebase Hosting
    step {
      name = "gcr.io/firebase-tools"
      dir  = "frontend"
      args = [
        "deploy",
        "--project=${local.project_id}",
        "--only=hosting:${var.environment}"
      ]
    }
  }

  depends_on = [
    google_project_service.apis,
    null_resource.firebase_setup,
    google_cloud_run_service.fastapi_service
  ]
}

# Manual trigger for Frontend deployment
resource "google_cloudbuild_trigger" "frontend_manual" {
  name        = "${local.project_id}-${var.environment}-frontend-manual"
  description = "Manual trigger to deploy the frontend"
  project     = local.project_id
  
  # Only create if we're not in check-only mode
  count = var.check_only ? 0 : 1

  # GitHub configuration
  github {
    owner = coalesce(var.github_owner, local.github_user)
    name  = coalesce(var.github_repo, local.github_repo)
    
    # Manual trigger
    pull_request {
      branch = var.trigger_branch
      comment_control = "COMMENTS_ENABLED"
    }
  }

  # Include/exclude specific file paths
  included_files = [
    "frontend/**",
    "project_config.yml"
  ]

  # Build configuration with the same dynamic URL approach
  build {
    # Step 1: Install dependencies
    step {
      name = "node:16"
      dir  = "frontend"
      entrypoint = "npm"
      args = ["install"]
    }

    # Step 2: Get the Cloud Run URL
    step {
      name = "gcr.io/google.com/cloudsdktool/cloud-sdk"
      entrypoint = "bash"
      args = [
        "-c",
        "gcloud run services describe ${local.project_id}-${var.environment} --region=${var.gcp_region} --format='value(status.url)' > /workspace/api_url.txt"
      ]
    }

    # Step 3: Build the frontend with the actual Cloud Run URL
    step {
      name = "node:16"
      dir  = "frontend"
      entrypoint = "bash"
      args = [
        "-c",
        "API_URL=$(cat /workspace/api_url.txt) && npm run build -- --env=NEXT_PUBLIC_API_URL=$API_URL --env=NEXT_PUBLIC_ENV=${var.environment}"
      ]
    }

    # Step 4: Deploy to Firebase Hosting
    step {
      name = "gcr.io/firebase-tools"
      dir  = "frontend"
      args = [
        "deploy",
        "--project=${local.project_id}",
        "--only=hosting:${var.environment}"
      ]
    }
  }

  depends_on = [
    google_project_service.apis,
    null_resource.firebase_setup,
    google_cloud_run_service.fastapi_service
  ]
} 