#!/bin/bash

# SaveLife.com Cloud Synchronization Script
# This script synchronizes local development environment with cloud resources

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="$PROJECT_ROOT/.cloud-sync-config"

# Cloud configurations
AWS_PROFILE="savelife-dev"
AWS_REGION="us-east-1"
GCP_PROJECT="savelife-platform"
GCP_REGION="us-central1"
AZURE_RESOURCE_GROUP="savelife-dev-rg"
AZURE_LOCATION="eastus"

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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to load configuration
load_config() {
    if [ -f "$CONFIG_FILE" ]; then
        source "$CONFIG_FILE"
        print_status "Loaded configuration from $CONFIG_FILE"
    else
        print_warning "No configuration file found. Using defaults."
    fi
}

# Function to save configuration
save_config() {
    cat > "$CONFIG_FILE" << EOF
# SaveLife.com Cloud Sync Configuration
AWS_PROFILE="$AWS_PROFILE"
AWS_REGION="$AWS_REGION"
GCP_PROJECT="$GCP_PROJECT"
GCP_REGION="$GCP_REGION"
AZURE_RESOURCE_GROUP="$AZURE_RESOURCE_GROUP"
AZURE_LOCATION="$AZURE_LOCATION"
LAST_SYNC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
EOF
    print_status "Configuration saved to $CONFIG_FILE"
}

# Function to check cloud authentication
check_cloud_auth() {
    print_step "Checking cloud authentication..."
    
    local auth_issues=0
    
    # Check AWS authentication
    if command_exists aws; then
        if aws sts get-caller-identity --profile "$AWS_PROFILE" >/dev/null 2>&1; then
            local aws_account=$(aws sts get-caller-identity --profile "$AWS_PROFILE" --query Account --output text)
            print_status "AWS authenticated (Account: $aws_account)"
        else
            print_warning "AWS authentication failed. Run: aws configure --profile $AWS_PROFILE"
            auth_issues=$((auth_issues + 1))
        fi
    else
        print_warning "AWS CLI not installed"
        auth_issues=$((auth_issues + 1))
    fi
    
    # Check GCP authentication
    if command_exists gcloud; then
        if gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
            local gcp_account=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n1)
            print_status "GCP authenticated (Account: $gcp_account)"
            gcloud config set project "$GCP_PROJECT" >/dev/null 2>&1
        else
            print_warning "GCP authentication failed. Run: gcloud auth login"
            auth_issues=$((auth_issues + 1))
        fi
    else
        print_warning "Google Cloud CLI not installed"
        auth_issues=$((auth_issues + 1))
    fi
    
    # Check Azure authentication
    if command_exists az; then
        if az account show >/dev/null 2>&1; then
            local azure_account=$(az account show --query user.name --output tsv)
            print_status "Azure authenticated (Account: $azure_account)"
        else
            print_warning "Azure authentication failed. Run: az login"
            auth_issues=$((auth_issues + 1))
        fi
    else
        print_warning "Azure CLI not installed"
        auth_issues=$((auth_issues + 1))
    fi
    
    if [ $auth_issues -gt 0 ]; then
        print_error "Please resolve authentication issues before continuing"
        exit 1
    fi
}

# Function to sync environment variables from cloud
sync_environment_variables() {
    print_step "Syncing environment variables from cloud..."
    
    local env_file="$PROJECT_ROOT/backend/.env.cloud"
    echo "# Cloud-synced environment variables" > "$env_file"
    echo "# Last sync: $(date)" >> "$env_file"
    echo "" >> "$env_file"
    
    # Sync from AWS Parameter Store
    if command_exists aws; then
        print_status "Syncing from AWS Parameter Store..."
        
        # Get database URL from AWS Secrets Manager
        if aws secretsmanager describe-secret --secret-id "savelife/database-url" --profile "$AWS_PROFILE" >/dev/null 2>&1; then
            local db_url=$(aws secretsmanager get-secret-value \
                --secret-id "savelife/database-url" \
                --profile "$AWS_PROFILE" \
                --query SecretString --output text)
            echo "DATABASE_URL_CLOUD=\"$db_url\"" >> "$env_file"
        fi
        
        # Get other secrets
        for secret in "openai-api-key" "stripe-secret-key" "jwt-secret"; do
            if aws secretsmanager describe-secret --secret-id "savelife/$secret" --profile "$AWS_PROFILE" >/dev/null 2>&1; then
                local value=$(aws secretsmanager get-secret-value \
                    --secret-id "savelife/$secret" \
                    --profile "$AWS_PROFILE" \
                    --query SecretString --output text)
                local var_name=$(echo "$secret" | tr '[:lower:]' '[:upper:]' | tr '-' '_')
                echo "${var_name}_CLOUD=\"$value\"" >> "$env_file"
            fi
        done
    fi
    
    # Sync from GCP Secret Manager
    if command_exists gcloud; then
        print_status "Syncing from GCP Secret Manager..."
        
        for secret in "database-password" "openai-api-key" "stripe-secret-key" "jwt-secret"; do
            if gcloud secrets describe "$secret" >/dev/null 2>&1; then
                local value=$(gcloud secrets versions access latest --secret="$secret")
                local var_name=$(echo "$secret" | tr '[:lower:]' '[:upper:]' | tr '-' '_')
                echo "${var_name}_GCP=\"$value\"" >> "$env_file"
            fi
        done
    fi
    
    # Sync from Azure Key Vault
    if command_exists az; then
        print_status "Syncing from Azure Key Vault..."
        
        local key_vault="savelife-dev-kv"
        if az keyvault show --name "$key_vault" --resource-group "$AZURE_RESOURCE_GROUP" >/dev/null 2>&1; then
            for secret in "database-password" "openai-api-key" "stripe-secret-key"; do
                if az keyvault secret show --vault-name "$key_vault" --name "$secret" >/dev/null 2>&1; then
                    local value=$(az keyvault secret show \
                        --vault-name "$key_vault" \
                        --name "$secret" \
                        --query value --output tsv)
                    local var_name=$(echo "$secret" | tr '[:lower:]' '[:upper:]' | tr '-' '_')
                    echo "${var_name}_AZURE=\"$value\"" >> "$env_file"
                fi
            done
        fi
    fi
    
    print_status "Environment variables synced to $env_file"
}

# Function to sync database schemas
sync_database_schemas() {
    print_step "Syncing database schemas..."
    
    local schemas_dir="$PROJECT_ROOT/database/schemas"
    mkdir -p "$schemas_dir"
    
    # Export local schema
    if command_exists pg_dump; then
        print_status "Exporting local database schema..."
        pg_dump -h localhost -U savelife -d savelife_dev --schema-only > "$schemas_dir/local_schema.sql"
    fi
    
    # Sync from AWS RDS
    if command_exists aws; then
        print_status "Getting AWS RDS schema..."
        local rds_endpoint=$(aws rds describe-db-instances \
            --profile "$AWS_PROFILE" \
            --query "DBInstances[?DBName=='savelife'].Endpoint.Address" \
            --output text)
        
        if [ -n "$rds_endpoint" ]; then
            # Note: This would require proper network access and credentials
            echo "-- AWS RDS endpoint: $rds_endpoint" > "$schemas_dir/aws_schema_info.sql"
        fi
    fi
    
    # Sync from GCP Cloud SQL
    if command_exists gcloud; then
        print_status "Getting GCP Cloud SQL schema..."
        local instances=$(gcloud sql instances list --format="value(name)" --filter="name:savelife")
        
        if [ -n "$instances" ]; then
            echo "-- GCP Cloud SQL instances:" > "$schemas_dir/gcp_schema_info.sql"
            echo "$instances" >> "$schemas_dir/gcp_schema_info.sql"
        fi
    fi
    
    # Sync from Azure Database
    if command_exists az; then
        print_status "Getting Azure Database schema..."
        local servers=$(az postgres server list \
            --resource-group "$AZURE_RESOURCE_GROUP" \
            --query "[].name" --output tsv)
        
        if [ -n "$servers" ]; then
            echo "-- Azure PostgreSQL servers:" > "$schemas_dir/azure_schema_info.sql"
            echo "$servers" >> "$schemas_dir/azure_schema_info.sql"
        fi
    fi
    
    print_status "Database schemas synced to $schemas_dir"
}

# Function to sync container images
sync_container_images() {
    print_step "Syncing container images..."
    
    local images_file="$PROJECT_ROOT/.cloud-images"
    echo "# Cloud container images" > "$images_file"
    echo "# Last sync: $(date)" >> "$images_file"
    echo "" >> "$images_file"
    
    # Get AWS ECR images
    if command_exists aws; then
        print_status "Getting AWS ECR images..."
        
        local repositories=$(aws ecr describe-repositories \
            --profile "$AWS_PROFILE" \
            --query "repositories[?contains(repositoryName, 'savelife')].repositoryName" \
            --output text)
        
        for repo in $repositories; do
            local latest_tag=$(aws ecr describe-images \
                --profile "$AWS_PROFILE" \
                --repository-name "$repo" \
                --query "sort_by(imageDetails, &imagePushedAt)[-1].imageTags[0]" \
                --output text)
            
            if [ "$latest_tag" != "None" ]; then
                local registry=$(aws sts get-caller-identity --profile "$AWS_PROFILE" --query Account --output text)
                echo "AWS_${repo//-/_}=${registry}.dkr.ecr.${AWS_REGION}.amazonaws.com/${repo}:${latest_tag}" >> "$images_file"
            fi
        done
    fi
    
    # Get GCP Artifact Registry images
    if command_exists gcloud; then
        print_status "Getting GCP Artifact Registry images..."
        
        local repositories=$(gcloud artifacts repositories list \
            --location="$GCP_REGION" \
            --format="value(name)" \
            --filter="name:savelife")
        
        for repo in $repositories; do
            local repo_name=$(basename "$repo")
            echo "GCP_${repo_name//-/_}=${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT}/${repo_name}" >> "$images_file"
        done
    fi
    
    # Get Azure Container Registry images
    if command_exists az; then
        print_status "Getting Azure Container Registry images..."
        
        local registries=$(az acr list \
            --resource-group "$AZURE_RESOURCE_GROUP" \
            --query "[].name" --output tsv)
        
        for registry in $registries; do
            local repositories=$(az acr repository list \
                --name "$registry" \
                --output tsv)
            
            for repo in $repositories; do
                echo "AZURE_${repo//-/_}=${registry}.azurecr.io/${repo}:latest" >> "$images_file"
            done
        done
    fi
    
    print_status "Container images synced to $images_file"
}

# Function to sync infrastructure state
sync_infrastructure_state() {
    print_step "Syncing infrastructure state..."
    
    local state_dir="$PROJECT_ROOT/infrastructure/state"
    mkdir -p "$state_dir"
    
    # Get AWS CloudFormation stacks
    if command_exists aws; then
        print_status "Getting AWS CloudFormation stacks..."
        
        aws cloudformation list-stacks \
            --profile "$AWS_PROFILE" \
            --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE \
            --query "StackSummaries[?contains(StackName, 'savelife')]" \
            > "$state_dir/aws_stacks.json"
    fi
    
    # Get GCP Deployment Manager deployments
    if command_exists gcloud; then
        print_status "Getting GCP Deployment Manager deployments..."
        
        gcloud deployment-manager deployments list \
            --format=json \
            --filter="name:savelife" \
            > "$state_dir/gcp_deployments.json" 2>/dev/null || echo "[]" > "$state_dir/gcp_deployments.json"
    fi
    
    # Get Azure Resource Manager deployments
    if command_exists az; then
        print_status "Getting Azure Resource Manager deployments..."
        
        az deployment group list \
            --resource-group "$AZURE_RESOURCE_GROUP" \
            --query "[?contains(name, 'savelife')]" \
            > "$state_dir/azure_deployments.json"
    fi
    
    print_status "Infrastructure state synced to $state_dir"
}

# Function to sync monitoring and logs
sync_monitoring_logs() {
    print_step "Syncing monitoring and logs..."
    
    local logs_dir="$PROJECT_ROOT/logs/cloud"
    mkdir -p "$logs_dir"
    
    # Get AWS CloudWatch logs
    if command_exists aws; then
        print_status "Getting AWS CloudWatch log groups..."
        
        aws logs describe-log-groups \
            --profile "$AWS_PROFILE" \
            --log-group-name-prefix "/aws/ecs/savelife" \
            --query "logGroups[].logGroupName" \
            > "$logs_dir/aws_log_groups.json"
    fi
    
    # Get GCP Cloud Logging
    if command_exists gcloud; then
        print_status "Getting GCP Cloud Logging info..."
        
        gcloud logging sinks list \
            --format=json \
            --filter="name:savelife" \
            > "$logs_dir/gcp_log_sinks.json" 2>/dev/null || echo "[]" > "$logs_dir/gcp_log_sinks.json"
    fi
    
    # Get Azure Monitor logs
    if command_exists az; then
        print_status "Getting Azure Monitor workspaces..."
        
        az monitor log-analytics workspace list \
            --resource-group "$AZURE_RESOURCE_GROUP" \
            --query "[?contains(name, 'savelife')]" \
            > "$logs_dir/azure_workspaces.json"
    fi
    
    print_status "Monitoring and logs info synced to $logs_dir"
}

# Function to update local configuration
update_local_config() {
    print_step "Updating local configuration..."
    
    # Update docker-compose with cloud image references
    if [ -f "$PROJECT_ROOT/.cloud-images" ]; then
        print_status "Updating docker-compose with cloud images..."
        
        # Create cloud-specific docker-compose file
        cat > "$PROJECT_ROOT/docker-compose.cloud.yml" << EOF
version: '3.8'

# Cloud-synced configuration
# This file is auto-generated by cloud-sync.sh

services:
  frontend:
    image: \${CLOUD_FRONTEND_IMAGE:-savelifeprod.azurecr.io/frontend:latest}
    environment:
      - REACT_APP_API_URL=\${CLOUD_API_URL:-http://localhost:5000}
      - REACT_APP_ENVIRONMENT=cloud-sync

  backend:
    image: \${CLOUD_BACKEND_IMAGE:-savelifeprod.azurecr.io/backend:latest}
    environment:
      - DATABASE_URL=\${DATABASE_URL_CLOUD:-postgresql://savelife:password@localhost:5432/savelife_dev}
      - OPENAI_API_KEY=\${OPENAI_API_KEY_CLOUD}
      - STRIPE_SECRET_KEY=\${STRIPE_SECRET_KEY_CLOUD}
EOF
    fi
    
    # Update VS Code settings with cloud configurations
    local vscode_dir="$PROJECT_ROOT/.vscode"
    if [ -d "$vscode_dir" ]; then
        print_status "Updating VS Code settings..."
        
        # Add cloud-specific settings
        cat >> "$vscode_dir/settings.json.cloud" << EOF
{
    "aws.profile": "$AWS_PROFILE",
    "gcp.project": "$GCP_PROJECT",
    "azure.resourceGroups": ["$AZURE_RESOURCE_GROUP"],
    "docker.defaultRegistryPath": "savelifeprod.azurecr.io"
}
EOF
    fi
    
    print_status "Local configuration updated"
}

# Function to generate sync report
generate_sync_report() {
    print_step "Generating sync report..."
    
    local report_file="$PROJECT_ROOT/cloud-sync-report.md"
    
    cat > "$report_file" << EOF
# SaveLife.com Cloud Sync Report

**Generated:** $(date)
**Last Sync:** $(date -u +%Y-%m-%dT%H:%M:%SZ)

## Cloud Authentication Status

$(if command_exists aws && aws sts get-caller-identity --profile "$AWS_PROFILE" >/dev/null 2>&1; then
    echo "- ✅ AWS: Authenticated ($(aws sts get-caller-identity --profile "$AWS_PROFILE" --query Account --output text))"
else
    echo "- ❌ AWS: Not authenticated"
fi)

$(if command_exists gcloud && gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "- ✅ GCP: Authenticated ($(gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n1))"
else
    echo "- ❌ GCP: Not authenticated"
fi)

$(if command_exists az && az account show >/dev/null 2>&1; then
    echo "- ✅ Azure: Authenticated ($(az account show --query user.name --output tsv))"
else
    echo "- ❌ Azure: Not authenticated"
fi)

## Synced Resources

### Environment Variables
- Location: \`backend/.env.cloud\`
- Contains cloud-sourced secrets and configuration

### Database Schemas
- Location: \`database/schemas/\`
- Local and cloud schema information

### Container Images
- Location: \`.cloud-images\`
- Latest image references from all cloud providers

### Infrastructure State
- Location: \`infrastructure/state/\`
- Current deployment status across clouds

### Monitoring & Logs
- Location: \`logs/cloud/\`
- Log group and monitoring configuration info

## Next Steps

1. Review synced environment variables in \`backend/.env.cloud\`
2. Update local \`.env\` files with required values
3. Test local development environment
4. Deploy changes using CI/CD pipelines

## Commands

- Start with cloud config: \`docker-compose -f docker-compose.yml -f docker-compose.cloud.yml up\`
- View cloud images: \`cat .cloud-images\`
- Check sync status: \`./scripts/cloud-sync.sh --status\`

EOF
    
    print_status "Sync report generated: $report_file"
}

# Function to show sync status
show_sync_status() {
    print_step "Cloud Sync Status"
    
    if [ -f "$CONFIG_FILE" ]; then
        source "$CONFIG_FILE"
        echo "Last sync: $LAST_SYNC"
    else
        echo "No previous sync found"
    fi
    
    echo
    echo "Cloud Authentication:"
    
    if command_exists aws && aws sts get-caller-identity --profile "$AWS_PROFILE" >/dev/null 2>&1; then
        echo "  AWS: ✅ Authenticated"
    else
        echo "  AWS: ❌ Not authenticated"
    fi
    
    if command_exists gcloud && gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        echo "  GCP: ✅ Authenticated"
    else
        echo "  GCP: ❌ Not authenticated"
    fi
    
    if command_exists az && az account show >/dev/null 2>&1; then
        echo "  Azure: ✅ Authenticated"
    else
        echo "  Azure: ❌ Not authenticated"
    fi
    
    echo
    echo "Synced Files:"
    [ -f "$PROJECT_ROOT/backend/.env.cloud" ] && echo "  ✅ Environment variables" || echo "  ❌ Environment variables"
    [ -d "$PROJECT_ROOT/database/schemas" ] && echo "  ✅ Database schemas" || echo "  ❌ Database schemas"
    [ -f "$PROJECT_ROOT/.cloud-images" ] && echo "  ✅ Container images" || echo "  ❌ Container images"
    [ -d "$PROJECT_ROOT/infrastructure/state" ] && echo "  ✅ Infrastructure state" || echo "  ❌ Infrastructure state"
}

# Function to clean sync data
clean_sync_data() {
    print_step "Cleaning sync data..."
    
    rm -f "$PROJECT_ROOT/backend/.env.cloud"
    rm -f "$PROJECT_ROOT/.cloud-images"
    rm -f "$PROJECT_ROOT/docker-compose.cloud.yml"
    rm -rf "$PROJECT_ROOT/database/schemas"
    rm -rf "$PROJECT_ROOT/infrastructure/state"
    rm -rf "$PROJECT_ROOT/logs/cloud"
    rm -f "$PROJECT_ROOT/cloud-sync-report.md"
    rm -f "$CONFIG_FILE"
    
    print_status "Sync data cleaned"
}

# Function to display help
show_help() {
    cat << EOF
SaveLife.com Cloud Synchronization Script

Usage: $0 [OPTION]

Options:
  --full          Perform full synchronization (default)
  --env           Sync environment variables only
  --db            Sync database schemas only
  --images        Sync container images only
  --infra         Sync infrastructure state only
  --logs          Sync monitoring and logs only
  --status        Show sync status
  --clean         Clean all sync data
  --help          Show this help message

Examples:
  $0                    # Full sync
  $0 --env             # Sync environment variables only
  $0 --status          # Show current sync status
  $0 --clean           # Clean all synced data

EOF
}

# Main function
main() {
    cd "$PROJECT_ROOT"
    load_config
    
    case "${1:-}" in
        --env)
            check_cloud_auth
            sync_environment_variables
            save_config
            ;;
        --db)
            check_cloud_auth
            sync_database_schemas
            save_config
            ;;
        --images)
            check_cloud_auth
            sync_container_images
            save_config
            ;;
        --infra)
            check_cloud_auth
            sync_infrastructure_state
            save_config
            ;;
        --logs)
            check_cloud_auth
            sync_monitoring_logs
            save_config
            ;;
        --status)
            show_sync_status
            ;;
        --clean)
            clean_sync_data
            ;;
        --help)
            show_help
            ;;
        *)
            # Full sync
            check_cloud_auth
            sync_environment_variables
            sync_database_schemas
            sync_container_images
            sync_infrastructure_state
            sync_monitoring_logs
            update_local_config
            generate_sync_report
            save_config
            print_status "Full cloud synchronization completed!"
            ;;
    esac
}

# Run main function
main "$@"

