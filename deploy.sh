#!/bin/bash

# Deployment script for wb-python-fastapi-accelerator
# Usage: ./deploy.sh [staging|production]

# Default to staging environment
ENVIRONMENT=${1:-staging}

echo "Deploying to $ENVIRONMENT environment..."

# Set project ID
PROJECT_ID="wb-python-fastapi-accelerator"

# Ensure we're authenticated
gcloud auth login --quiet
gcloud config set project $PROJECT_ID

# Deploy backend
echo "Building and deploying backend..."
cd backend

# Build and push Docker image
IMAGE_NAME="gcr.io/$PROJECT_ID/$PROJECT_ID-api:$ENVIRONMENT"
docker build -t $IMAGE_NAME .
docker push $IMAGE_NAME

# Deploy to Cloud Run
gcloud run deploy "$PROJECT_ID-$ENVIRONMENT" \
  --image $IMAGE_NAME \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars="ENV=$ENVIRONMENT,FIRESTORE_PROJECT_ID=$PROJECT_ID,FIRESTORE_COLLECTION_PREFIX=$ENVIRONMENT"

# Get the deployed URL
BACKEND_URL=$(gcloud run services describe "$PROJECT_ID-$ENVIRONMENT" --region=us-central1 --format='value(status.url)')
echo "Backend deployed to: $BACKEND_URL"

# Go back to root directory
cd ..

# Deploy frontend
echo "Building and deploying frontend..."
cd frontend

# Install dependencies if needed
npm install

# Build the frontend with the environment-specific API URL
echo "Building frontend with API URL: $BACKEND_URL"
NEXT_PUBLIC_API_URL=$BACKEND_URL NEXT_PUBLIC_ENV=$ENVIRONMENT npm run build
 
# Deploy to Firebase Hosting
firebase use $PROJECT_ID
firebase deploy --only hosting:$ENVIRONMENT

# Output the frontend URL
if [ "$ENVIRONMENT" == "production" ]; then
  FRONTEND_URL="https://$PROJECT_ID.web.app"
else
  FRONTEND_URL="https://$PROJECT_ID-$ENVIRONMENT.web.app"
fi

echo "Frontend deployed to: $FRONTEND_URL"
echo "Deployment completed successfully!" 