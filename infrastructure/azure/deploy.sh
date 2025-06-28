#!/bin/bash

# SaveLife.com Azure Deployment Script
# This script deploys the SaveLife platform to Azure using ARM templates and Azure Container Registry

set -e

# Configuration
RESOURCE_GROUP="savelife-prod-rg"
LOCATION="East US"
ENVIRONMENT="prod"
DOMAIN_NAME="savelife.com"
SUBSCRIPTION_ID=""

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
    
    if ! command -v az &> /dev/null; then
        print_error "Azure CLI is not installed. Please install it first."
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install it first."
        exit 1
    fi
    
    print_status "All dependencies are installed."
}

# Check Azure authentication
check_azure_auth() {
    print_status "Checking Azure authentication..."
    
    if ! az account show &> /dev/null; then
        print_error "Not authenticated with Azure. Please run 'az login' first."
        exit 1
    fi
    
    ACCOUNT=$(az account show --query user.name --output tsv)
    SUBSCRIPTION_ID=$(az account show --query id --output tsv)
    print_status "Using Azure Account: $ACCOUNT"
    print_status "Subscription ID: $SUBSCRIPTION_ID"
}

# Create resource group
create_resource_group() {
    print_step "Creating resource group..."
    
    az group create \
        --name $RESOURCE_GROUP \
        --location "$LOCATION" \
        --tags Environment=$ENVIRONMENT Project=SaveLife
    
    print_status "Resource group created successfully."
}

# Get sensitive parameters
get_parameters() {
    print_step "Collecting deployment parameters..."
    
    # Prompt for sensitive parameters
    read -s -p "Enter database password: " DB_PASSWORD
    echo
    read -s -p "Enter OpenAI API key: " OPENAI_API_KEY
    echo
    read -s -p "Enter Stripe secret key: " STRIPE_SECRET_KEY
    echo
    
    print_status "Parameters collected successfully."
}

# Deploy ARM template
deploy_infrastructure() {
    print_step "Deploying Azure infrastructure..."
    
    DEPLOYMENT_NAME="savelife-deployment-$(date +%Y%m%d-%H%M%S)"
    
    az deployment group create \
        --resource-group $RESOURCE_GROUP \
        --template-file savelife-infrastructure.json \
        --parameters \
            environment=$ENVIRONMENT \
            location="$LOCATION" \
            domainName=$DOMAIN_NAME \
            databasePassword="$DB_PASSWORD" \
            openAIApiKey="$OPENAI_API_KEY" \
            stripeSecretKey="$STRIPE_SECRET_KEY" \
        --name $DEPLOYMENT_NAME
    
    print_status "Infrastructure deployed successfully."
}

# Get deployment outputs
get_deployment_outputs() {
    print_step "Getting deployment outputs..."
    
    CONTAINER_REGISTRY=$(az deployment group show \
        --resource-group $RESOURCE_GROUP \
        --name $DEPLOYMENT_NAME \
        --query properties.outputs.containerRegistryName.value \
        --output tsv)
    
    FRONTEND_APP=$(az deployment group show \
        --resource-group $RESOURCE_GROUP \
        --name $DEPLOYMENT_NAME \
        --query properties.outputs.frontendAppName.value \
        --output tsv)
    
    BACKEND_APP=$(az deployment group show \
        --resource-group $RESOURCE_GROUP \
        --name $DEPLOYMENT_NAME \
        --query properties.outputs.backendAppName.value \
        --output tsv)
    
    print_status "Deployment outputs retrieved successfully."
}

# Build and push Docker images
build_and_push_images() {
    print_step "Building and pushing Docker images..."
    
    # Login to Azure Container Registry
    az acr login --name $CONTAINER_REGISTRY
    
    # Build and push frontend
    print_status "Building frontend image..."
    cd ../../frontend
    docker build -t $CONTAINER_REGISTRY.azurecr.io/frontend:latest .
    docker push $CONTAINER_REGISTRY.azurecr.io/frontend:latest
    
    # Build and push backend
    print_status "Building backend image..."
    cd ../backend
    docker build -t $CONTAINER_REGISTRY.azurecr.io/backend:latest .
    docker push $CONTAINER_REGISTRY.azurecr.io/backend:latest
    
    cd ../infrastructure/azure
    print_status "Docker images built and pushed successfully."
}

# Restart web apps to pull new images
restart_web_apps() {
    print_step "Restarting web applications..."
    
    # Restart frontend app
    az webapp restart \
        --resource-group $RESOURCE_GROUP \
        --name $FRONTEND_APP
    
    # Restart backend app
    az webapp restart \
        --resource-group $RESOURCE_GROUP \
        --name $BACKEND_APP
    
    print_status "Web applications restarted successfully."
}

# Configure custom domain (optional)
configure_custom_domain() {
    print_step "Configuring custom domain..."
    
    if [ "$DOMAIN_NAME" != "savelife.com" ]; then
        print_warning "Skipping custom domain configuration for non-production domain."
        return
    fi
    
    # Get Application Gateway public IP
    APP_GATEWAY_IP=$(az deployment group show \
        --resource-group $RESOURCE_GROUP \
        --name $DEPLOYMENT_NAME \
        --query properties.outputs.applicationGatewayPublicIP.value \
        --output tsv)
    
    print_status "Application Gateway IP: $APP_GATEWAY_IP"
    print_warning "Please update your DNS records:"
    echo "  - A record for $DOMAIN_NAME pointing to $APP_GATEWAY_IP"
    echo "  - A record for www.$DOMAIN_NAME pointing to $APP_GATEWAY_IP"
    echo "  - A record for api.$DOMAIN_NAME pointing to $APP_GATEWAY_IP"
}

# Set up monitoring and alerts
setup_monitoring() {
    print_step "Setting up monitoring and alerts..."
    
    # Create action group for notifications
    az monitor action-group create \
        --resource-group $RESOURCE_GROUP \
        --name "savelife-alerts" \
        --short-name "savelife" || true
    
    # Create metric alerts
    az monitor metrics alert create \
        --resource-group $RESOURCE_GROUP \
        --name "High CPU Usage" \
        --description "Alert when CPU usage is high" \
        --severity 2 \
        --condition "avg Percentage CPU > 80" \
        --scopes "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Web/sites/$FRONTEND_APP" \
        --action "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/microsoft.insights/actionGroups/savelife-alerts" || true
    
    az monitor metrics alert create \
        --resource-group $RESOURCE_GROUP \
        --name "High Memory Usage" \
        --description "Alert when memory usage is high" \
        --severity 2 \
        --condition "avg MemoryPercentage > 80" \
        --scopes "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Web/sites/$BACKEND_APP" \
        --action "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/microsoft.insights/actionGroups/savelife-alerts" || true
    
    print_status "Monitoring and alerts configured successfully."
}

# Configure backup and disaster recovery
setup_backup() {
    print_step "Setting up backup and disaster recovery..."
    
    # Enable backup for web apps
    STORAGE_ACCOUNT=$(az deployment group show \
        --resource-group $RESOURCE_GROUP \
        --name $DEPLOYMENT_NAME \
        --query properties.outputs.storageAccountName.value \
        --output tsv)
    
    # Create backup configuration for frontend
    az webapp config backup update \
        --resource-group $RESOURCE_GROUP \
        --webapp-name $FRONTEND_APP \
        --container-url "https://$STORAGE_ACCOUNT.blob.core.windows.net/backups" \
        --frequency 1 \
        --retain-one true \
        --retention 30 || true
    
    # Create backup configuration for backend
    az webapp config backup update \
        --resource-group $RESOURCE_GROUP \
        --webapp-name $BACKEND_APP \
        --container-url "https://$STORAGE_ACCOUNT.blob.core.windows.net/backups" \
        --frequency 1 \
        --retain-one true \
        --retention 30 || true
    
    print_status "Backup and disaster recovery configured successfully."
}

# Run health checks
run_health_checks() {
    print_step "Running health checks..."
    
    FRONTEND_URL=$(az deployment group show \
        --resource-group $RESOURCE_GROUP \
        --name $DEPLOYMENT_NAME \
        --query properties.outputs.frontendUrl.value \
        --output tsv)
    
    BACKEND_URL=$(az deployment group show \
        --resource-group $RESOURCE_GROUP \
        --name $DEPLOYMENT_NAME \
        --query properties.outputs.backendUrl.value \
        --output tsv)
    
    # Wait for applications to start
    print_status "Waiting for applications to start..."
    sleep 60
    
    # Check frontend health
    if curl -f -s "$FRONTEND_URL" > /dev/null; then
        print_status "Frontend health check: PASSED"
    else
        print_warning "Frontend health check: FAILED"
    fi
    
    # Check backend health
    if curl -f -s "$BACKEND_URL/api/ai/health" > /dev/null; then
        print_status "Backend health check: PASSED"
    else
        print_warning "Backend health check: FAILED"
    fi
}

# Get final deployment information
get_deployment_info() {
    print_step "Getting final deployment information..."
    
    FRONTEND_URL=$(az deployment group show \
        --resource-group $RESOURCE_GROUP \
        --name $DEPLOYMENT_NAME \
        --query properties.outputs.frontendUrl.value \
        --output tsv)
    
    BACKEND_URL=$(az deployment group show \
        --resource-group $RESOURCE_GROUP \
        --name $DEPLOYMENT_NAME \
        --query properties.outputs.backendUrl.value \
        --output tsv)
    
    APP_GATEWAY_IP=$(az deployment group show \
        --resource-group $RESOURCE_GROUP \
        --name $DEPLOYMENT_NAME \
        --query properties.outputs.applicationGatewayPublicIP.value \
        --output tsv)
    
    print_status "Deployment completed successfully!"
    echo
    echo "=== Deployment Information ==="
    echo "Resource Group: $RESOURCE_GROUP"
    echo "Location: $LOCATION"
    echo "Environment: $ENVIRONMENT"
    echo "Frontend URL: $FRONTEND_URL"
    echo "Backend URL: $BACKEND_URL"
    echo "Application Gateway IP: $APP_GATEWAY_IP"
    echo "Container Registry: $CONTAINER_REGISTRY.azurecr.io"
    echo
    echo "Next steps:"
    echo "1. Update your DNS records to point to $APP_GATEWAY_IP"
    echo "2. Configure SSL certificates in Application Gateway"
    echo "3. Test the application at $FRONTEND_URL"
    echo "4. Monitor the deployment in Azure Portal"
}

# Main deployment function
main() {
    print_status "Starting SaveLife.com Azure deployment..."
    
    check_dependencies
    check_azure_auth
    get_parameters
    create_resource_group
    deploy_infrastructure
    get_deployment_outputs
    build_and_push_images
    restart_web_apps
    configure_custom_domain
    setup_monitoring
    setup_backup
    run_health_checks
    get_deployment_info
    
    print_status "Deployment completed successfully!"
}

# Run main function
main "$@"

