#!/bin/bash

# VERA Deployment Script for Google Cloud Run
# This script deploys VERA to Cloud Run without requiring Secret Manager
# Users will provide their own API keys via the Streamlit UI

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID=${1:-""}
REGION=${2:-"europe-central2"}
SERVICE_NAME="vera"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}-app"

echo "🚀 VERA Deployment Script"
echo "================================"

# Check if project ID is provided
if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}❌ Error: Project ID is required${NC}"
    echo "Usage: ./deploy.sh PROJECT_ID [REGION]"
    echo "Example: ./deploy.sh my-project-id europe-central2"
    exit 1
fi

echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Service Name: $SERVICE_NAME"
echo ""

# Set project
echo "📋 Setting project..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable run.googleapis.com \
    cloudbuild.googleapis.com \
    containerregistry.googleapis.com

# Build and push Docker image
echo "🐳 Building Docker image..."
echo "This may take several minutes..."
gcloud builds submit --tag $IMAGE_NAME

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 900 \
    --max-instances 10 \
    --min-instances 0 \
    --port 8080

# Get service URL
echo -e "${GREEN}🌐 Service URL:${NC} $SERVICE_URL"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Open the URL above to access VERA"
echo "  2. Monitor logs: gcloud run services logs tail $SERVICE_NAME --region $REGION"
echo "  3. View metrics in Cloud Console"
echo ""
