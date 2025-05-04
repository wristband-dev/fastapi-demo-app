# Firestore database setup
resource "google_firestore_database" "database" {
  project     = local.project_id
  name        = "(default)"
  location_id = var.firestore_location
  type        = "FIRESTORE_NATIVE"

  # Only create if we're not in check-only mode
  count = var.check_only ? 0 : 1
}

# Set up Firestore App Engine integration
resource "google_app_engine_application" "app" {
  project     = local.project_id
  location_id = "us-central"
  
  # Only create if we're not in check-only mode
  count = var.check_only ? 0 : 1
  
  # This is needed for Firestore
  database_type = "CLOUD_FIRESTORE"
  
  # Avoid conflicts with the Firestore database creation
  depends_on = [
    google_project.project
  ]
}

# Create Firebase hosting configuration
resource "null_resource" "firebase_hosting_setup" {
  count = var.check_only ? 0 : 1
  
  provisioner "local-exec" {
    command = <<EOT
      # Make sure firebase CLI is installed
      npm list -g firebase-tools || npm install -g firebase-tools
      
      # Set up firebase configuration
      mkdir -p ../frontend/.firebase
      
      # Create firebase.json with hosting configuration for different environments
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
      firebase use ${local.project_id} --non-interactive
      firebase hosting:sites:create ${local.project_id} --non-interactive || echo "Production site already exists"
      firebase hosting:sites:create ${local.project_id}-staging --non-interactive || echo "Staging site already exists"
    EOT
    interpreter = ["bash", "-c"]
  }
  
  depends_on = [
    null_resource.firebase_setup
  ]
}

# Firebase project setup
resource "null_resource" "firebase_setup" {
  count = var.check_only ? 0 : 1
  
  provisioner "local-exec" {
    command = <<EOT
      # Install the Firebase CLI if it's not already installed
      npm list -g firebase-tools || npm install -g firebase-tools
      
      # Add the Firebase to the project
      firebase projects:addfirebase ${local.project_id} --non-interactive || echo "Firebase already enabled"
      
      # Initialize Firestore rules and indexes if needed
      if [ ! -d "../backend/firebase" ]; then
        mkdir -p ../backend/firebase
        cd ../backend/firebase
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
        cat > firestore.indexes.json <<EOF
{
  "indexes": [],
  "fieldOverrides": []
}
EOF
      fi
      
      # Deploy Firestore rules
      cd ../backend/firebase || exit 1
      firebase use ${local.project_id} --non-interactive
      firebase deploy --only firestore:rules --non-interactive
    EOT
    interpreter = ["bash", "-c"]
  }
  
  # Depends on the Firestore database and App Engine being set up
  depends_on = [
    google_firestore_database.database,
    google_app_engine_application.app
  ]
} 