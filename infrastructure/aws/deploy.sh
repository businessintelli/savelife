#!/bin/bash

# SaveLife.com AWS Deployment Script
# This script deploys the SaveLife platform to AWS using CloudFormation and ECS

set -e

# Configuration
STACK_NAME="savelife-prod"
REGION="us-east-1"
ENVIRONMENT="prod"
DOMAIN_NAME="savelife.com"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Check if required tools are installed
check_dependencies() {
    print_status "Checking dependencies..."
    
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install it first."
        exit 1
    fi
    
    print_status "All dependencies are installed."
}

# Check AWS credentials
check_aws_credentials() {
    print_status "Checking AWS credentials..."
    
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS credentials are not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    print_status "Using AWS Account: $ACCOUNT_ID"
}

# Create ECR repositories
create_ecr_repositories() {
    print_status "Creating ECR repositories..."
    
    # Create frontend repository
    aws ecr describe-repositories --repository-names "${STACK_NAME}-frontend" --region $REGION &> /dev/null || \
    aws ecr create-repository --repository-name "${STACK_NAME}-frontend" --region $REGION
    
    # Create backend repository
    aws ecr describe-repositories --repository-names "${STACK_NAME}-backend" --region $REGION &> /dev/null || \
    aws ecr create-repository --repository-name "${STACK_NAME}-backend" --region $REGION
    
    print_status "ECR repositories created successfully."
}

# Build and push Docker images
build_and_push_images() {
    print_status "Building and pushing Docker images..."
    
    # Get ECR login token
    aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com
    
    # Build and push frontend
    print_status "Building frontend image..."
    cd ../../frontend
    docker build -t $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/${STACK_NAME}-frontend:latest .
    docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/${STACK_NAME}-frontend:latest
    
    # Build and push backend
    print_status "Building backend image..."
    cd ../backend
    docker build -t $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/${STACK_NAME}-backend:latest .
    docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/${STACK_NAME}-backend:latest
    
    cd ../infrastructure/aws
    print_status "Docker images built and pushed successfully."
}

# Request SSL certificate
request_ssl_certificate() {
    print_status "Checking for SSL certificate..."
    
    # Check if certificate already exists
    CERT_ARN=$(aws acm list-certificates --region $REGION --query "CertificateSummaryList[?DomainName=='$DOMAIN_NAME'].CertificateArn" --output text)
    
    if [ -z "$CERT_ARN" ]; then
        print_status "Requesting SSL certificate for $DOMAIN_NAME..."
        CERT_ARN=$(aws acm request-certificate \
            --domain-name $DOMAIN_NAME \
            --subject-alternative-names "*.${DOMAIN_NAME}" \
            --validation-method DNS \
            --region $REGION \
            --query CertificateArn --output text)
        
        print_warning "SSL certificate requested. Please validate it in the AWS Console before proceeding."
        print_warning "Certificate ARN: $CERT_ARN"
        read -p "Press enter when certificate validation is complete..."
    else
        print_status "Using existing SSL certificate: $CERT_ARN"
    fi
    
    echo $CERT_ARN
}

# Deploy CloudFormation stack
deploy_infrastructure() {
    local cert_arn=$1
    
    print_status "Deploying CloudFormation stack..."
    
    # Prompt for sensitive parameters
    read -s -p "Enter database password: " DB_PASSWORD
    echo
    read -s -p "Enter OpenAI API key: " OPENAI_API_KEY
    echo
    read -s -p "Enter Stripe secret key: " STRIPE_SECRET_KEY
    echo
    
    aws cloudformation deploy \
        --template-file savelife-infrastructure.yml \
        --stack-name $STACK_NAME \
        --parameter-overrides \
            Environment=$ENVIRONMENT \
            DomainName=$DOMAIN_NAME \
            CertificateArn=$cert_arn \
            DatabasePassword=$DB_PASSWORD \
            OpenAIApiKey=$OPENAI_API_KEY \
            StripeSecretKey=$STRIPE_SECRET_KEY \
        --capabilities CAPABILITY_IAM \
        --region $REGION
    
    print_status "CloudFormation stack deployed successfully."
}

# Update ECS services
update_ecs_services() {
    print_status "Updating ECS services..."
    
    # Force new deployment to pick up latest images
    aws ecs update-service \
        --cluster "${STACK_NAME}-cluster" \
        --service "${STACK_NAME}-frontend" \
        --force-new-deployment \
        --region $REGION > /dev/null
    
    aws ecs update-service \
        --cluster "${STACK_NAME}-cluster" \
        --service "${STACK_NAME}-backend" \
        --force-new-deployment \
        --region $REGION > /dev/null
    
    print_status "ECS services updated successfully."
}

# Get deployment outputs
get_deployment_outputs() {
    print_status "Getting deployment outputs..."
    
    ALB_DNS=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --query "Stacks[0].Outputs[?OutputKey=='LoadBalancerDNS'].OutputValue" \
        --output text)
    
    CLOUDFRONT_DOMAIN=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --query "Stacks[0].Outputs[?OutputKey=='CloudFrontDomainName'].OutputValue" \
        --output text)
    
    print_status "Deployment completed successfully!"
    echo
    echo "=== Deployment Information ==="
    echo "Stack Name: $STACK_NAME"
    echo "Region: $REGION"
    echo "Environment: $ENVIRONMENT"
    echo "Load Balancer DNS: $ALB_DNS"
    echo "CloudFront Domain: $CLOUDFRONT_DOMAIN"
    echo
    echo "Next steps:"
    echo "1. Update your DNS records to point $DOMAIN_NAME to $CLOUDFRONT_DOMAIN"
    echo "2. Wait for DNS propagation (may take up to 48 hours)"
    echo "3. Test the application at https://$DOMAIN_NAME"
}

# Main deployment function
main() {
    print_status "Starting SaveLife.com AWS deployment..."
    
    check_dependencies
    check_aws_credentials
    create_ecr_repositories
    build_and_push_images
    
    CERT_ARN=$(request_ssl_certificate)
    deploy_infrastructure $CERT_ARN
    update_ecs_services
    get_deployment_outputs
    
    print_status "Deployment completed successfully!"
}

# Run main function
main "$@"

