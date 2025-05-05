# Check if Firestore database already exists and prepare for creation if needed
resource "null_resource" "firestore_setup" {
  count = var.check_only ? 0 : 1
  
  provisioner "local-exec" {
    command = <<EOT
      # First check if Firestore app exists
      result=$(gcloud firestore databases list --project=${local.project_id} --format="value(name)" 2>/dev/null || echo "")
      
      if [ -n "$result" ]; then
        echo "Firestore database already exists, skipping creation"
      else
        echo "Creating Firestore database in us-central1..."
        gcloud firestore databases create --project=${local.project_id} --location=us-central1 --type=firestore-native || {
          echo "Failed to create Firestore database, may need to configure App Engine first"
          echo "Creating App Engine application..."
          gcloud app create --project=${local.project_id} --region=us-central || true
          
          # Try again after App Engine is created
          echo "Retrying Firestore database creation..."
          gcloud firestore databases create --project=${local.project_id} --location=us-central1 --type=firestore-native || echo "Failed to create Firestore database automatically. It may be created in another way."
        }
      fi
    EOT
    interpreter = ["bash", "-c"]
  }
  
  depends_on = [
    google_project_service.apis["firestore.googleapis.com"],
    google_project_service.apis["appengine.googleapis.com"],
    null_resource.verify_billing
  ]
}

# Set up Firestore App Engine integration only if needed
resource "google_app_engine_application" "app" {
  project     = local.project_id
  location_id = "us-central"
  
  # Only create if we're not in check-only mode
  count = var.check_only ? 0 : 1
  
  # This is needed for Firestore
  database_type = "CLOUD_FIRESTORE"
  
  # Avoid conflicts with the Firestore database creation
  depends_on = [
    google_project.project,
    google_project_service.apis["appengine.googleapis.com"]
  ]

  # Sometimes this fails if Firestore is already set up, so ignore errors
  lifecycle {
    ignore_changes = [location_id, database_type]
  }
}

# Firebase project setup
resource "null_resource" "firebase_setup" {
  # Only create if we're not in check-only mode
  count = var.check_only ? 0 : 1
  
  provisioner "local-exec" {
    command = <<EOT
      # Install the Firebase CLI if it's not already installed
      npm list -g firebase-tools || npm install -g firebase-tools
      
      # Add the Firebase to the project
      echo "Attempting to add Firebase to project ${local.project_id}..."
      firebase projects:addfirebase ${local.project_id} --non-interactive || echo "Firebase already enabled or couldn't be added"
      
      # Create necessary directories
      mkdir -p ../backend/firebase
      
      # Initialize Firestore rules and indexes
      echo "Creating Firestore rules in ../backend/firebase..."
      cd ../backend/firebase
      
      # Create firestore.rules
      cat > firestore.rules <<EOF
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if request.auth != null;
    }
  }
}
EOF
      
      # Create firestore.indexes.json
      cat > firestore.indexes.json <<EOF
{
  "indexes": [],
  "fieldOverrides": []
}
EOF
      
      # Attempt to deploy Firestore rules, but continue if it fails
      echo "Attempting to deploy Firestore rules..."
      firebase use ${local.project_id} --non-interactive || echo "Failed to set Firebase project"
      firebase deploy --only firestore:rules --non-interactive || echo "Failed to deploy Firestore rules, but continuing"
      
      echo "Firebase setup completed with available permissions"
    EOT
    interpreter = ["bash", "-c"]
  }
  
  # Depends on the Firestore database and App Engine being set up
  depends_on = [
    google_app_engine_application.app,
    null_resource.firestore_setup
  ]
}

# Create Firebase hosting configuration
resource "null_resource" "firebase_hosting_setup" {
  # Only create if we're not in check-only mode
  count = var.check_only ? 0 : 1
  
  provisioner "local-exec" {
    command = <<EOT
      # Make sure firebase CLI is installed
      npm list -g firebase-tools || npm install -g firebase-tools
      
      # Create necessary directories
      mkdir -p ../frontend/.firebase
      
      # Create firebase.json with hosting configuration for different environments
      echo "Creating Firebase hosting configuration..."
      cat > ../frontend/firebase.json <<EOF
{
  "hosting": {
    "public": "build",
    "ignore": [
      "firebase.json",
      "**/.*",
      "**/node_modules/**"
    ],
    "rewrites": [
      {
        "source": "**",
        "destination": "/index.html"
      }
    ],
    "targets": {
      "production": {
        "hosting": {
          "site": "${local.project_id}"
        }
      },
      "staging": {
        "hosting": {
          "site": "${local.project_id}-staging"
        }
      }
    }
  }
}
EOF

      # Create .firebaserc file linking to the project
      cat > ../frontend/.firebaserc <<EOF
{
  "projects": {
    "default": "${local.project_id}"
  },
  "targets": {
    "${local.project_id}": {
      "hosting": {
        "production": [
          "${local.project_id}"
        ],
        "staging": [
          "${local.project_id}-staging"
        ]
      }
    }
  }
}
EOF

      # Create or update Firebase hosting sites
      echo "Attempting to create Firebase hosting sites..."
      firebase use ${local.project_id} --non-interactive || echo "Failed to set Firebase project"
      firebase hosting:sites:create ${local.project_id} --non-interactive || echo "Production site already exists or couldn't be created"
      firebase hosting:sites:create ${local.project_id}-staging --non-interactive || echo "Staging site already exists or couldn't be created"
      
      echo "Firebase hosting setup completed with available permissions"
    EOT
    interpreter = ["bash", "-c"]
  }
  
  depends_on = [
    null_resource.firebase_setup,
    google_project_service.apis["firebase.googleapis.com"]
  ]
} 