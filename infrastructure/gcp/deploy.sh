#!/bin/bash

# SaveLife.com Google Cloud Platform Deployment Script
# This script deploys the SaveLife platform to GCP using Deployment Manager and Cloud Run

set -e

# Configuration
PROJECT_ID="savelife-platform"
REGION="us-central1"
ZONE="us-central1-a"
ENVIRONMENT="prod"
DOMAIN_NAME="savelife.com"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if required tools are installed
check_dependencies() {
    print_status "Checking dependencies..."
    
    if ! command -v gcloud &> /dev/null; then
        print_error "Google Cloud SDK is not installed. Please install it first."
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install it first."
        exit 1
    fi
    
    print_status "All dependencies are installed."
}

# Check GCP authentication
check_gcp_auth() {
    print_status "Checking GCP authentication..."
    
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        print_error "Not authenticated with Google Cloud. Please run 'gcloud auth login' first."
        exit 1
    fi
    
    ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n1)
    print_status "Using GCP Account: $ACCOUNT"
}

# Set up GCP project
setup_project() {
    print_step "Setting up GCP project..."
    
    # Set the project
    gcloud config set project $PROJECT_ID
    
    # Enable required APIs
    print_status "Enabling required APIs..."
    gcloud services enable \
        compute.googleapis.com \
        container.googleapis.com \
        cloudsql.googleapis.com \
        storage.googleapis.com \
        cloudresourcemanager.googleapis.com \
        iam.googleapis.com \
        secretmanager.googleapis.com \
        cloudbuild.googleapis.com \
        run.googleapis.com \
        monitoring.googleapis.com \
        logging.googleapis.com \
        deploymentmanager.googleapis.com
    
    print_status "Project setup completed."
}

# Create service accounts
create_service_accounts() {
    print_step "Creating service accounts..."
    
    # Backend service account
    gcloud iam service-accounts create savelife-backend \
        --display-name="SaveLife Backend Service Account" \
        --description="Service account for SaveLife backend services" || true
    
    # Grant necessary permissions
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:savelife-backend@${PROJECT_ID}.iam.gserviceaccount.com" \
        --role="roles/cloudsql.client"
    
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:savelife-backend@${PROJECT_ID}.iam.gserviceaccount.com" \
        --role="roles/storage.objectAdmin"
    
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:savelife-backend@${PROJECT_ID}.iam.gserviceaccount.com" \
        --role="roles/secretmanager.secretAccessor"
    
    print_status "Service accounts created successfully."
}

# Create secrets
create_secrets() {
    print_step "Creating secrets in Secret Manager..."
    
    # Prompt for sensitive information
    read -s -p "Enter database password: " DB_PASSWORD
    echo
    read -s -p "Enter OpenAI API key: " OPENAI_API_KEY
    echo
    read -s -p "Enter Stripe secret key: " STRIPE_SECRET_KEY
    echo
    
    # Create secrets
    echo -n "$DB_PASSWORD" | gcloud secrets create database-password --data-file=- || \
    echo -n "$DB_PASSWORD" | gcloud secrets versions add database-password --data-file=-
    
    echo -n "$OPENAI_API_KEY" | gcloud secrets create openai-api-key --data-file=- || \
    echo -n "$OPENAI_API_KEY" | gcloud secrets versions add openai-api-key --data-file=-
    
    echo -n "$STRIPE_SECRET_KEY" | gcloud secrets create stripe-secret-key --data-file=- || \
    echo -n "$STRIPE_SECRET_KEY" | gcloud secrets versions add stripe-secret-key --data-file=-
    
    # Generate JWT secret
    JWT_SECRET=$(openssl rand -base64 32)
    echo -n "$JWT_SECRET" | gcloud secrets create jwt-secret --data-file=- || \
    echo -n "$JWT_SECRET" | gcloud secrets versions add jwt-secret --data-file=-
    
    print_status "Secrets created successfully."
}

# Build and push Docker images
build_and_push_images() {
    print_step "Building and pushing Docker images..."
    
    # Configure Docker for GCR
    gcloud auth configure-docker
    
    # Build and push frontend
    print_status "Building frontend image..."
    cd ../../frontend
    docker build -t gcr.io/$PROJECT_ID/frontend:latest .
    docker push gcr.io/$PROJECT_ID/frontend:latest
    
    # Build and push backend
    print_status "Building backend image..."
    cd ../backend
    docker build -t gcr.io/$PROJECT_ID/backend:latest .
    docker push gcr.io/$PROJECT_ID/backend:latest
    
    cd ../infrastructure/gcp
    print_status "Docker images built and pushed successfully."
}

# Create Cloud SQL database
create_database() {
    print_step "Creating Cloud SQL database..."
    
    # Create Cloud SQL instance
    gcloud sql instances create savelife-db \
        --database-version=POSTGRES_15 \
        --tier=db-f1-micro \
        --region=$REGION \
        --storage-size=20GB \
        --storage-type=SSD \
        --backup-start-time=03:00 \
        --maintenance-window-day=SUN \
        --maintenance-window-hour=04 \
        --enable-bin-log || true
    
    # Create database
    gcloud sql databases create savelife --instance=savelife-db || true
    
    # Create user
    DB_PASSWORD=$(gcloud secrets versions access latest --secret="database-password")
    gcloud sql users create savelife \
        --instance=savelife-db \
        --password="$DB_PASSWORD" || true
    
    print_status "Cloud SQL database created successfully."
}

# Create storage buckets
create_storage() {
    print_step "Creating Cloud Storage buckets..."
    
    # Static assets bucket
    gsutil mb -p $PROJECT_ID -c STANDARD -l US gs://savelife-static-assets || true
    gsutil iam ch allUsers:objectViewer gs://savelife-static-assets
    
    # Documents bucket
    gsutil mb -p $PROJECT_ID -c STANDARD -l US gs://savelife-documents || true
    
    # Backups bucket
    gsutil mb -p $PROJECT_ID -c NEARLINE -l US gs://savelife-backups || true
    
    print_status "Storage buckets created successfully."
}

# Deploy Cloud Run services
deploy_cloud_run() {
    print_step "Deploying Cloud Run services..."
    
    # Get database connection name
    DB_CONNECTION=$(gcloud sql instances describe savelife-db --format="value(connectionName)")
    
    # Create database URL secret
    DB_PASSWORD=$(gcloud secrets versions access latest --secret="database-password")
    DATABASE_URL="postgresql://savelife:${DB_PASSWORD}@/${PROJECT_ID}:${REGION}:savelife-db/savelife"
    echo -n "$DATABASE_URL" | gcloud secrets create database-url --data-file=- || \
    echo -n "$DATABASE_URL" | gcloud secrets versions add database-url --data-file=-
    
    # Deploy backend service
    print_status "Deploying backend service..."
    gcloud run deploy savelife-backend \
        --image=gcr.io/$PROJECT_ID/backend:latest \
        --platform=managed \
        --region=$REGION \
        --allow-unauthenticated \
        --service-account=savelife-backend@${PROJECT_ID}.iam.gserviceaccount.com \
        --add-cloudsql-instances=$DB_CONNECTION \
        --set-secrets=DATABASE_URL=database-url:latest,OPENAI_API_KEY=openai-api-key:latest,STRIPE_SECRET_KEY=stripe-secret-key:latest,JWT_SECRET=jwt-secret:latest \
        --set-env-vars=ENVIRONMENT=production,GCS_BUCKET_DOCUMENTS=savelife-documents,GCS_BUCKET_STATIC=savelife-static-assets \
        --memory=2Gi \
        --cpu=2 \
        --concurrency=80 \
        --max-instances=20 \
        --min-instances=2
    
    # Deploy frontend service
    print_status "Deploying frontend service..."
    BACKEND_URL=$(gcloud run services describe savelife-backend --platform=managed --region=$REGION --format="value(status.url)")
    
    gcloud run deploy savelife-frontend \
        --image=gcr.io/$PROJECT_ID/frontend:latest \
        --platform=managed \
        --region=$REGION \
        --allow-unauthenticated \
        --set-env-vars=REACT_APP_API_URL=$BACKEND_URL,REACT_APP_ENVIRONMENT=production \
        --memory=512Mi \
        --cpu=1 \
        --concurrency=80 \
        --max-instances=10 \
        --min-instances=1
    
    print_status "Cloud Run services deployed successfully."
}

# Set up load balancer and SSL
setup_load_balancer() {
    print_step "Setting up load balancer and SSL..."
    
    # Create managed SSL certificate
    gcloud compute ssl-certificates create savelife-ssl-cert \
        --domains=$DOMAIN_NAME,www.$DOMAIN_NAME,api.$DOMAIN_NAME \
        --global || true
    
    # Get Cloud Run service URLs
    FRONTEND_URL=$(gcloud run services describe savelife-frontend --platform=managed --region=$REGION --format="value(status.url)")
    BACKEND_URL=$(gcloud run services describe savelife-backend --platform=managed --region=$REGION --format="value(status.url)")
    
    # Create network endpoint groups
    gcloud compute network-endpoint-groups create savelife-frontend-neg \
        --region=$REGION \
        --network-endpoint-type=serverless \
        --cloud-run-service=savelife-frontend || true
    
    gcloud compute network-endpoint-groups create savelife-backend-neg \
        --region=$REGION \
        --network-endpoint-type=serverless \
        --cloud-run-service=savelife-backend || true
    
    # Create backend services
    gcloud compute backend-services create savelife-frontend-backend-service \
        --global \
        --protocol=HTTPS || true
    
    gcloud compute backend-services add-backend savelife-frontend-backend-service \
        --global \
        --network-endpoint-group=savelife-frontend-neg \
        --network-endpoint-group-region=$REGION || true
    
    gcloud compute backend-services create savelife-backend-backend-service \
        --global \
        --protocol=HTTPS || true
    
    gcloud compute backend-services add-backend savelife-backend-backend-service \
        --global \
        --network-endpoint-group=savelife-backend-neg \
        --network-endpoint-group-region=$REGION || true
    
    # Create URL map
    gcloud compute url-maps create savelife-url-map \
        --default-service=savelife-frontend-backend-service || true
    
    gcloud compute url-maps add-path-matcher savelife-url-map \
        --path-matcher-name=api-matcher \
        --default-service=savelife-backend-backend-service \
        --path-rules="/api/*=savelife-backend-backend-service" || true
    
    gcloud compute url-maps add-host-rule savelife-url-map \
        --hosts=api.$DOMAIN_NAME \
        --path-matcher=api-matcher || true
    
    # Create target HTTPS proxy
    gcloud compute target-https-proxies create savelife-target-proxy \
        --url-map=savelife-url-map \
        --ssl-certificates=savelife-ssl-cert || true
    
    # Create global forwarding rule
    gcloud compute forwarding-rules create savelife-lb \
        --global \
        --target-https-proxy=savelife-target-proxy \
        --ports=443 || true
    
    print_status "Load balancer and SSL setup completed."
}

# Get deployment outputs
get_deployment_outputs() {
    print_step "Getting deployment outputs..."
    
    FRONTEND_URL=$(gcloud run services describe savelife-frontend --platform=managed --region=$REGION --format="value(status.url)")
    BACKEND_URL=$(gcloud run services describe savelife-backend --platform=managed --region=$REGION --format="value(status.url)")
    LB_IP=$(gcloud compute forwarding-rules describe savelife-lb --global --format="value(IPAddress)")
    
    print_status "Deployment completed successfully!"
    echo
    echo "=== Deployment Information ==="
    echo "Project ID: $PROJECT_ID"
    echo "Region: $REGION"
    echo "Environment: $ENVIRONMENT"
    echo "Frontend URL: $FRONTEND_URL"
    echo "Backend URL: $BACKEND_URL"
    echo "Load Balancer IP: $LB_IP"
    echo
    echo "Next steps:"
    echo "1. Update your DNS records:"
    echo "   - A record for $DOMAIN_NAME pointing to $LB_IP"
    echo "   - A record for www.$DOMAIN_NAME pointing to $LB_IP"
    echo "   - A record for api.$DOMAIN_NAME pointing to $LB_IP"
    echo "2. Wait for DNS propagation and SSL certificate provisioning (may take up to 60 minutes)"
    echo "3. Test the application at https://$DOMAIN_NAME"
}

# Main deployment function
main() {
    print_status "Starting SaveLife.com GCP deployment..."
    
    check_dependencies
    check_gcp_auth
    setup_project
    create_service_accounts
    create_secrets
    build_and_push_images
    create_database
    create_storage
    deploy_cloud_run
    setup_load_balancer
    get_deployment_outputs
    
    print_status "Deployment completed successfully!"
}

# Run main function
main "$@"

