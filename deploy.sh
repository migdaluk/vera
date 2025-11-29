#!/bin/bash
# VERA - Quick Deployment Script for Google Cloud Run
# Usage: ./deploy.sh [PROJECT_ID]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 VERA Deployment Script${NC}"
echo "================================"

# Check if PROJECT_ID is provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: PROJECT_ID not provided${NC}"
    echo "Usage: ./deploy.sh [PROJECT_ID]"
    exit 1
fi

PROJECT_ID=$1
REGION="europe-central2"
SERVICE_NAME="vera"
IMAGE_NAME="gcr.io/$PROJECT_ID/vera-app"

echo -e "${YELLOW}Project ID:${NC} $PROJECT_ID"
echo -e "${YELLOW}Region:${NC} $REGION"
echo -e "${YELLOW}Service Name:${NC} $SERVICE_NAME"
echo ""

# Set project
echo -e "${GREEN}📋 Setting project...${NC}"
gcloud config set project $PROJECT_ID

# Enable required APIs
echo -e "${GREEN}🔧 Enabling required APIs...${NC}"
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable secretmanager.googleapis.com

# Check if API key secret exists
echo -e "${GREEN}🔑 Checking for API key secret...${NC}"
if ! gcloud secrets describe google-api-key &> /dev/null; then
    echo -e "${YELLOW}Secret 'google-api-key' not found.${NC}"
    echo -e "${YELLOW}Please create it manually:${NC}"
    echo "  echo -n 'YOUR_API_KEY' | gcloud secrets create google-api-key --data-file=-"
    echo ""
    read -p "Press Enter once you've created the secret..."
fi

# Build and push image
echo -e "${GREEN}🏗️  Building and pushing Docker image...${NC}"
gcloud builds submit --tag $IMAGE_NAME

# Deploy to Cloud Run
echo -e "${GREEN}🚢 Deploying to Cloud Run...${NC}"
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-secrets GOOGLE_API_KEY=google-api-key:latest \
  --memory 2Gi \
  --cpu 2 \
  --timeout 900 \
  --max-instances 10 \
  --min-instances 0

# Get service URL
echo ""
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)')
echo -e "${GREEN}🌐 Service URL:${NC} $SERVICE_URL"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Open the URL above to access VERA"
echo "  2. Monitor logs: gcloud run services logs tail $SERVICE_NAME --region $REGION"
echo "  3. View metrics in Cloud Console"
echo ""
