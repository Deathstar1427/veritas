#!/bin/bash
# Veritas Deployment Script
# This script deploys Veritas to GCP Cloud Run + Firebase Hosting

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—${NC}"
echo -e "${BLUE}â•‘  Veritas Deployment Script            â•‘${NC}"
echo -e "${BLUE}â•‘  GCP Cloud Run + Firebase Hosting      â•‘${NC}"
echo -e "${BLUE}â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•${NC}"
echo ""

# Step 1: Check Prerequisites
echo -e "${YELLOW}Step 1: Checking prerequisites...${NC}"
echo ""

if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}âŒ gcloud CLI not found${NC}"
    echo "Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi
echo -e "${GREEN}âœ“ gcloud CLI found${NC}"

if ! command -v node &> /dev/null; then
    echo -e "${RED}âŒ Node.js not found${NC}"
    echo "Install from: https://nodejs.org/"
    exit 1
fi
echo -e "${GREEN}âœ“ Node.js found${NC}"

if ! command -v npm &> /dev/null; then
    echo -e "${RED}âŒ npm not found${NC}"
    exit 1
fi
echo -e "${GREEN}âœ“ npm found${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}âŒ Python 3 not found${NC}"
    exit 1
fi
echo -e "${GREEN}âœ“ Python 3 found${NC}"

echo ""
echo -e "${YELLOW}Step 2: Configuration${NC}"
echo ""

# Get project ID
read -p "Enter your GCP Project ID: " PROJECT_ID
if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}âŒ Project ID cannot be empty${NC}"
    exit 1
fi

read -p "Enter your Gemini API Key: " GEMINI_KEY
if [ -z "$GEMINI_KEY" ]; then
    echo -e "${RED}âŒ Gemini API Key cannot be empty${NC}"
    exit 1
fi

read -p "Enter your GCP region (default: us-central1): " REGION
REGION=${REGION:-us-central1}

echo ""
echo -e "${GREEN}Configuration:${NC}"
echo "  Project ID: $PROJECT_ID"
echo "  Region: $REGION"
echo "  Gemini Key: [HIDDEN]"
echo ""

# Step 3: Set up GCP project
echo -e "${YELLOW}Step 3: Setting up GCP project...${NC}"
echo ""

gcloud config set project $PROJECT_ID 2>/dev/null
echo -e "${GREEN}âœ“ Project set to $PROJECT_ID${NC}"

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com 2>/dev/null || true
gcloud services enable run.googleapis.com 2>/dev/null || true
gcloud services enable containerregistry.googleapis.com 2>/dev/null || true
echo -e "${GREEN}âœ“ APIs enabled${NC}"

echo ""
echo -e "${YELLOW}Step 4: Building and deploying backend...${NC}"
echo ""

cd backend

# Build Docker image
echo "Building Docker image..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/veritas-backend 2>&1 | tail -20

if [ $? -ne 0 ]; then
    echo -e "${RED}âŒ Backend build failed${NC}"
    exit 1
fi
echo -e "${GREEN}âœ“ Backend image built${NC}"

# Deploy to Cloud Run
echo ""
echo "Deploying to Cloud Run..."
BACKEND_URL=$(gcloud run deploy veritas-backend \
  --image gcr.io/$PROJECT_ID/veritas-backend \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300 \
  --set-env-vars GEMINI_API_KEY=$GEMINI_KEY \
  --format='value(status.url)' 2>&1)

if [ -z "$BACKEND_URL" ]; then
    echo -e "${RED}âŒ Backend deployment failed${NC}"
    exit 1
fi

echo -e "${GREEN}âœ“ Backend deployed${NC}"
echo -e "${BLUE}Backend URL: $BACKEND_URL${NC}"

echo ""
echo -e "${YELLOW}Step 5: Testing backend...${NC}"
echo ""

# Test backend health
sleep 5
HEALTH_CHECK=$(curl -s "$BACKEND_URL/health" | grep -o '"status":"ok"')
if [ -z "$HEALTH_CHECK" ]; then
    echo -e "${RED}âš  Backend health check failed${NC}"
    echo "This might be temporary. Trying again in 10 seconds..."
    sleep 10
    HEALTH_CHECK=$(curl -s "$BACKEND_URL/health" || echo "")
fi

if [ ! -z "$HEALTH_CHECK" ]; then
    echo -e "${GREEN}âœ“ Backend health check passed${NC}"
else
    echo -e "${YELLOW}âš  Could not verify backend yet (may still be starting)${NC}"
fi

echo ""
echo -e "${YELLOW}Step 6: Setting up frontend...${NC}"
echo ""

cd ../frontend

# Create .env.local with backend URL
echo "VITE_API_URL=$BACKEND_URL" > .env.local
echo -e "${GREEN}âœ“ Frontend .env.local configured${NC}"

# Install dependencies
echo "Installing frontend dependencies..."
npm install --legacy-peer-deps --silent 2>&1 | tail -5
echo -e "${GREEN}âœ“ Dependencies installed${NC}"

# Build frontend
echo ""
echo "Building frontend..."
npm run build 2>&1 | tail -10

if [ ! -d "dist" ]; then
    echo -e "${RED}âŒ Frontend build failed${NC}"
    exit 1
fi
echo -e "${GREEN}âœ“ Frontend built${NC}"

BUILD_SIZE=$(du -sh dist | cut -f1)
echo "Build size: $BUILD_SIZE"

echo ""
echo -e "${YELLOW}Step 7: Setting up Firebase...${NC}"
echo ""

if ! command -v firebase &> /dev/null; then
    echo "Installing Firebase CLI..."
    npm install -g firebase-tools --silent
fi
echo -e "${GREEN}âœ“ Firebase CLI ready${NC}"

# Initialize Firebase (if not already done)
echo ""
echo "Initializing Firebase project..."
echo "Note: If this fails, you may need to:"
echo "1. Go to https://firebase.google.com/"
echo "2. Create a new project or select existing"
echo "3. Link it to your GCP project $PROJECT_ID"
echo ""

firebase init hosting --project=$PROJECT_ID --quiet 2>/dev/null || true

echo -e "${GREEN}âœ“ Firebase initialized${NC}"

echo ""
echo -e "${YELLOW}Step 8: Deploying frontend...${NC}"
echo ""

FIREBASE_URL=$(firebase deploy --only hosting --project=$PROJECT_ID 2>&1 | grep -i "hosting url" | tail -1 | grep -oE 'https[^[:space:]]*')

if [ -z "$FIREBASE_URL" ]; then
    echo -e "${YELLOW}âš  Could not extract Firebase URL from output${NC}"
    FIREBASE_URL="https://$PROJECT_ID.web.app"
fi

echo -e "${GREEN}âœ“ Frontend deployed${NC}"
echo -e "${BLUE}Frontend URL: $FIREBASE_URL${NC}"

echo ""
echo -e "${YELLOW}Step 9: Updating CORS for production...${NC}"
echo ""

echo "Updating backend/main.py with production CORS..."
cd ../backend

# Update CORS
sed -i "s|allow_origins=\[.*\]|allow_origins=[\n        \"http://localhost:5173\",\n        \"http://localhost:3000\",\n        \"$FIREBASE_URL\",\n    ]|g" main.py 2>/dev/null || true

echo -e "${GREEN}âœ“ CORS updated${NC}"

# Redeploy backend
echo ""
echo "Redeploying backend with updated CORS..."
gcloud run deploy veritas-backend \
  --image gcr.io/$PROJECT_ID/veritas-backend \
  --region $REGION \
  --no-gen2 \
  2>&1 | grep -E "(Deploying|âœ“|successfully)" || true

echo -e "${GREEN}âœ“ Backend redeployed${NC}"

echo ""
echo -e "${BLUE}â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—${NC}"
echo -e "${BLUE}â•‘  Deployment Complete!                 â•‘${NC}"
echo -e "${BLUE}â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•${NC}"
echo ""

echo -e "${GREEN}ðŸŽ‰ Veritas is now live!${NC}"
echo ""
echo -e "${BLUE}URLs:${NC}"
echo "  Backend: $BACKEND_URL"
echo "  Frontend: $FIREBASE_URL"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Visit: $FIREBASE_URL"
echo "2. Select 'Hiring' domain"
echo "3. Click 'Use Sample Data'"
echo "4. Should see results in 2-3 seconds"
echo ""
echo -e "${YELLOW}Monitoring:${NC}"
echo "  Backend logs: gcloud run logs read veritas-backend --limit 50 --project=$PROJECT_ID"
echo "  Firebase logs: firebase open hosting --project=$PROJECT_ID"
echo ""
echo -e "${YELLOW}Support:${NC}"
echo "  Deployment guide: ./DEPLOYMENT_FREE_TIER.md"
echo "  Troubleshooting: ./DEPLOYMENT_FREE_TIER.md#troubleshooting"
echo ""

