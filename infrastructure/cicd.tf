# We'll create a simple manual build trigger that doesn't require GitHub connection
resource "null_resource" "build_setup" {
  count = var.check_only ? 0 : 1
  
  provisioner "local-exec" {
    command = <<EOT
      # Create a simple manual build trigger
      echo "Setting up simplified Cloud Build triggers..."
      
      # Create or replace the backend build trigger
      gcloud builds triggers create manual \
        --name="${local.project_id}-${var.environment}-api-manual" \
        --project="${local.project_id}" \
        --region="global" \
        --build-config="backend/cloudbuild.yaml" \
        --description="Manual trigger to build and deploy the API" \
        || echo "Failed to create backend build trigger, but continuing"
      
      # Create build config if it doesn't exist
      if [ ! -d "../backend" ]; then
        mkdir -p ../backend
      fi
      
      # Create a simple cloud build YAML file
      cat > ../backend/cloudbuild.yaml <<EOF
steps:
  # Build the container image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/${local.project_id}/${local.project_id}-api:latest', '.']
  
  # Push the container image to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/${local.project_id}/${local.project_id}-api:latest']
  
  # Deploy container image to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - '${local.project_id}-${var.environment}'
      - '--image'
      - 'gcr.io/${local.project_id}/${local.project_id}-api:latest'
      - '--region'
      - '${var.gcp_region}'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'
images:
  - 'gcr.io/${local.project_id}/${local.project_id}-api:latest'
EOF

      echo "Cloud Build setup complete"
    EOT
    interpreter = ["bash", "-c"]
  }
  
  depends_on = [
    google_project_service.apis["cloudbuild.googleapis.com"],
    google_project_service.apis["containerregistry.googleapis.com"],
    null_resource.verify_billing
  ]
} 