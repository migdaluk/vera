# VERA - Google Cloud Deployment Guide

This guide explains how to deploy VERA (Virtual Evidence & Reality Assessment) to Google Cloud Platform.

## Deployment Options

### Recommended: Cloud Run (Serverless)
- ✅ **Best for**: Production deployment, auto-scaling
- ✅ **Pros**: Serverless, pay-per-use, auto-scaling, HTTPS out of the box
- ✅ **Cons**: Cold starts (mitigated with min instances)

### Alternative: Compute Engine (VM)
- ⚠️ **Best for**: Development, testing, custom requirements
- ⚠️ **Pros**: Full control, persistent storage
- ⚠️ **Cons**: Manual scaling, higher cost, more maintenance

---

## Prerequisites

1. **Google Cloud Account** with billing enabled
2. **Google Cloud Project** created
3. **gcloud CLI** installed ([Install Guide](https://cloud.google.com/sdk/docs/install))
4. **Docker** installed locally (for testing)
5. **Google AI Studio API Key** ([Get Key](https://aistudio.google.com/app/apikey))

---

## Option 1: Cloud Run Deployment (Recommended)

### Step 1: Prepare Your Project

#### 1.1 Create Dockerfile

Create `Dockerfile` in project root:

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY vera/ ./vera/
COPY .streamlit/ ./.streamlit/

# Create logs directory
RUN mkdir -p logs logs/agents logs/sessions

# Expose Streamlit port
EXPOSE 8080

# Set environment variables
ENV STREAMLIT_SERVER_PORT=8080
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ENV PYTHONPATH=/app

# Run Streamlit
CMD ["streamlit", "run", "vera/main.py", "--server.port=8080", "--server.address=0.0.0.0"]
```

#### 1.2 Create .dockerignore

Create `.dockerignore` to exclude unnecessary files:

```
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info/
dist/
build/
.git/
.gitignore
.venv/
venv/
env/
logs/
*.log
.DS_Store
.vscode/
.idea/
*.md
!README.md
docs/
tests/
```

#### 1.3 Create .streamlit/config.toml

Ensure Streamlit configuration exists:

```toml
[server]
port = 8080
address = "0.0.0.0"
headless = true

[browser]
gatherUsageStats = false
serverAddress = "0.0.0.0"
serverPort = 8080
```

### Step 2: Build and Test Locally

```bash
# Build Docker image
docker build -t vera-app .

# Test locally
docker run -p 8080:8080 \
  -e GOOGLE_API_KEY="your-api-key-here" \
  vera-app

# Open http://localhost:8080
```

### Step 3: Deploy to Cloud Run

#### 3.1 Enable Required APIs

```bash
# Set your project ID
export PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

#### 3.2 Build and Push to Container Registry

```bash
# Build and push using Cloud Build
gcloud builds submit --tag gcr.io/$PROJECT_ID/vera-app

# Or use Artifact Registry (recommended for new projects)
gcloud builds submit --tag europe-central2-docker.pkg.dev/$PROJECT_ID/vera/vera-app
```

#### 3.3 Deploy to Cloud Run

```bash
# Deploy to Cloud Run (no API key needed - users provide their own)
gcloud run deploy vera \
  --image gcr.io/$PROJECT_ID/vera-app \
  --platform managed \
  --region europe-central2 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 900 \
  --max-instances 10 \
  --min-instances 0 \
  --port 8080

# Note: 
# - No API key needed in deployment (users provide via UI)
# - min-instances=0 saves costs (cold starts acceptable)
# - Increase min-instances to 1 for faster response (costs more)
```

### Step 4: Access Your Application

After deployment, Cloud Run will provide a URL:
```
https://vera-HASH-uc.a.run.app
```

---

## Option 2: Compute Engine Deployment

### Step 1: Create VM Instance

```bash
gcloud compute instances create vera-vm \
  --zone=europe-central2-a \
  --machine-type=e2-medium \
  --image-family=debian-11 \
  --image-project=debian-cloud \
  --boot-disk-size=20GB \
  --tags=http-server,https-server
```

### Step 2: SSH and Setup

```bash
# SSH into VM
gcloud compute ssh vera-vm --zone=europe-central2-a

# Install dependencies
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv git

# Clone your repository
git clone https://github.com/your-username/vera.git
cd vera

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Set environment variable
export GOOGLE_API_KEY="your-api-key-here"

# Run Streamlit
streamlit run vera/main.py --server.port 8080
```

### Step 3: Setup Firewall

```bash
# Allow traffic on port 8080
gcloud compute firewall-rules create allow-streamlit \
  --allow tcp:8080 \
  --target-tags http-server
```

### Step 4: Setup Systemd Service (Optional)

Create `/etc/systemd/system/vera.service`:

```ini
[Unit]
Description=VERA Streamlit App
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/home/your-username/vera
Environment="GOOGLE_API_KEY=your-api-key-here"
ExecStart=/home/your-username/vera/.venv/bin/streamlit run vera/main.py --server.port 8080
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable vera
sudo systemctl start vera
```

---

## CI/CD with Cloud Build

### Create cloudbuild.yaml

```yaml
steps:
  # Build the container image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/vera-app', '.']
  
  # Push the container image to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/vera-app']
  
  # Deploy to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'vera'
      - '--image'
      - 'gcr.io/$PROJECT_ID/vera-app'
      - '--region'
      - 'europe-central2'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'
      - '--set-secrets'
      - 'GOOGLE_API_KEY=google-api-key:latest'

images:
  - 'gcr.io/$PROJECT_ID/vera-app'
```

### Setup Trigger

```bash
# Connect to GitHub repository
gcloud beta builds triggers create github \
  --repo-name=vera \
  --repo-owner=your-username \
  --branch-pattern="^main$" \
  --build-config=cloudbuild.yaml
```

---

## Monitoring and Logging

### View Logs

```bash
# Cloud Run logs
gcloud run services logs read vera --region europe-central2

# Stream logs
gcloud run services logs tail vera --region europe-central2
```

### Cloud Logging

Access logs in Cloud Console:
1. Go to **Logging** > **Logs Explorer**
2. Filter by resource: `Cloud Run Revision`
3. View structured JSON logs from VERA

### Monitoring Dashboard

1. Go to **Cloud Run** > **vera** > **Metrics**
2. Monitor:
   - Request count
   - Request latency
   - Container CPU/Memory utilization
   - Error rate

---

## Cost Optimization

### Cloud Run Pricing (Approximate)

- **CPU**: $0.00002400 per vCPU-second
- **Memory**: $0.00000250 per GiB-second
- **Requests**: $0.40 per million requests

**Example Monthly Cost** (100 requests/day, avg 60s per request):
- ~$5-10/month with min-instances=0
- ~$30-50/month with min-instances=1 (no cold starts)

### Tips to Reduce Costs

1. **Use min-instances=0** for development
2. **Set max-instances** to prevent runaway costs
3. **Enable Cloud CDN** for static assets
4. **Use Artifact Registry** (cheaper than Container Registry)

---

## Security Best Practices

### 1. API Key Security

VERA does not store API keys in the deployment. Users provide their own Google AI Studio API keys via the Streamlit UI sidebar. Keys are stored only in browser session memory and never persisted.

### 2. Enable Authentication

For production, enable IAM authentication:

```bash
gcloud run deploy vera \
  --no-allow-unauthenticated
```

Then grant access:
```bash
gcloud run services add-iam-policy-binding vera \
  --member="user:email@example.com" \
  --role="roles/run.invoker"
```

### 3. Use VPC Connector

For accessing private resources:

```bash
gcloud run deploy vera \
  --vpc-connector=your-connector \
  --vpc-egress=private-ranges-only
```

### 4. Enable Binary Authorization

Ensure only verified images are deployed.

---

## Troubleshooting

### Issue: Cold Starts

**Solution**: Set `--min-instances 1`

### Issue: Timeout Errors

**Solution**: Increase timeout:
```bash
gcloud run deploy vera --timeout 900
```

### Issue: Out of Memory

**Solution**: Increase memory:
```bash
gcloud run deploy vera --memory 4Gi
```

### Issue: API Key Not Found

**Solution**: Verify secret is accessible:
```bash
gcloud secrets versions access latest --secret=google-api-key
```

---

## Next Steps

1. ✅ Deploy to Cloud Run
2. ✅ Setup monitoring and alerts
3. ✅ Configure custom domain (optional)
4. ✅ Enable Cloud CDN (optional)
5. ✅ Setup CI/CD pipeline
6. ✅ Implement authentication (for production)

---

## Support

For issues or questions:
- Check Cloud Run logs: `gcloud run services logs read vera`
- Review [Cloud Run Documentation](https://cloud.google.com/run/docs)
- Check VERA logs in `logs/` directory

---

*Last updated: 2025-11-29*
