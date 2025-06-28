#!/bin/bash

# SaveLife.com Development Workflow Script
# This script provides a unified interface for common development tasks

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
BACKEND_DIR="$PROJECT_ROOT/backend"

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

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}=== $1 ===${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if services are running
check_services() {
    local services_running=true
    
    # Check if Docker is running
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running"
        services_running=false
    fi
    
    # Check if database is accessible
    if ! docker-compose ps postgres | grep -q "Up"; then
        print_warning "PostgreSQL container is not running"
        services_running=false
    fi
    
    # Check if Redis is accessible
    if ! docker-compose ps redis | grep -q "Up"; then
        print_warning "Redis container is not running"
        services_running=false
    fi
    
    if [ "$services_running" = false ]; then
        print_step "Starting required services..."
        docker-compose up -d postgres redis
        sleep 5
    fi
}

# Function to start development environment
start_dev() {
    print_header "Starting Development Environment"
    cd "$PROJECT_ROOT"
    
    check_services
    
    # Start backend
    print_step "Starting backend server..."
    cd "$BACKEND_DIR"
    if [ -d "venv" ]; then
        source venv/bin/activate
        python src/main.py &
        BACKEND_PID=$!
        echo $BACKEND_PID > /tmp/savelife_backend.pid
        print_status "Backend started (PID: $BACKEND_PID)"
    else
        print_error "Backend virtual environment not found. Run setup first."
        exit 1
    fi
    
    # Start frontend
    print_step "Starting frontend server..."
    cd "$FRONTEND_DIR"
    if [ -f "package.json" ]; then
        pnpm run dev &
        FRONTEND_PID=$!
        echo $FRONTEND_PID > /tmp/savelife_frontend.pid
        print_status "Frontend started (PID: $FRONTEND_PID)"
    else
        print_error "Frontend package.json not found. Run setup first."
        exit 1
    fi
    
    cd "$PROJECT_ROOT"
    
    print_success "Development environment started!"
    echo
    echo "Services:"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend:  http://localhost:5000"
    echo "  Database: postgresql://savelife:password@localhost:5432/savelife_dev"
    echo "  Redis:    redis://localhost:6379/0"
    echo
    echo "To stop: $0 stop"
}

# Function to stop development environment
stop_dev() {
    print_header "Stopping Development Environment"
    
    # Stop frontend
    if [ -f "/tmp/savelife_frontend.pid" ]; then
        local frontend_pid=$(cat /tmp/savelife_frontend.pid)
        if kill -0 "$frontend_pid" 2>/dev/null; then
            kill "$frontend_pid"
            print_status "Frontend stopped"
        fi
        rm -f /tmp/savelife_frontend.pid
    fi
    
    # Stop backend
    if [ -f "/tmp/savelife_backend.pid" ]; then
        local backend_pid=$(cat /tmp/savelife_backend.pid)
        if kill -0 "$backend_pid" 2>/dev/null; then
            kill "$backend_pid"
            print_status "Backend stopped"
        fi
        rm -f /tmp/savelife_backend.pid
    fi
    
    # Kill any remaining processes
    pkill -f "pnpm run dev" 2>/dev/null || true
    pkill -f "python src/main.py" 2>/dev/null || true
    
    # Stop Docker services
    cd "$PROJECT_ROOT"
    docker-compose down
    
    print_success "Development environment stopped!"
}

# Function to restart development environment
restart_dev() {
    print_header "Restarting Development Environment"
    stop_dev
    sleep 2
    start_dev
}

# Function to check development environment status
status_dev() {
    print_header "Development Environment Status"
    
    # Check Docker services
    echo "Docker Services:"
    docker-compose ps
    echo
    
    # Check development servers
    echo "Development Servers:"
    if [ -f "/tmp/savelife_frontend.pid" ]; then
        local frontend_pid=$(cat /tmp/savelife_frontend.pid)
        if kill -0 "$frontend_pid" 2>/dev/null; then
            echo "  Frontend: Running (PID: $frontend_pid)"
        else
            echo "  Frontend: Stopped"
        fi
    else
        echo "  Frontend: Stopped"
    fi
    
    if [ -f "/tmp/savelife_backend.pid" ]; then
        local backend_pid=$(cat /tmp/savelife_backend.pid)
        if kill -0 "$backend_pid" 2>/dev/null; then
            echo "  Backend: Running (PID: $backend_pid)"
        else
            echo "  Backend: Stopped"
        fi
    else
        echo "  Backend: Stopped"
    fi
    
    echo
    
    # Check service connectivity
    echo "Service Connectivity:"
    if curl -s http://localhost:3000 >/dev/null; then
        echo "  Frontend: ✅ Accessible"
    else
        echo "  Frontend: ❌ Not accessible"
    fi
    
    if curl -s http://localhost:5000/api/ai/health >/dev/null; then
        echo "  Backend: ✅ Accessible"
    else
        echo "  Backend: ❌ Not accessible"
    fi
    
    if pg_isready -h localhost -p 5432 -U savelife >/dev/null 2>&1; then
        echo "  Database: ✅ Accessible"
    else
        echo "  Database: ❌ Not accessible"
    fi
    
    if redis-cli -h localhost -p 6379 ping >/dev/null 2>&1; then
        echo "  Redis: ✅ Accessible"
    else
        echo "  Redis: ❌ Not accessible"
    fi
}

# Function to run tests
run_tests() {
    print_header "Running Tests"
    cd "$PROJECT_ROOT"
    
    local test_type="${1:-all}"
    local exit_code=0
    
    case "$test_type" in
        "frontend"|"fe")
            print_step "Running frontend tests..."
            cd "$FRONTEND_DIR"
            pnpm run test:ci || exit_code=$?
            pnpm run lint || exit_code=$?
            pnpm run type-check || exit_code=$?
            ;;
        "backend"|"be")
            print_step "Running backend tests..."
            cd "$BACKEND_DIR"
            source venv/bin/activate
            python -m pytest tests/ --cov=src --cov-report=html || exit_code=$?
            python -m flake8 src/ || exit_code=$?
            python -m mypy src/ || exit_code=$?
            ;;
        "integration"|"e2e")
            print_step "Running integration tests..."
            cd "$FRONTEND_DIR"
            pnpm run test:e2e || exit_code=$?
            ;;
        "all")
            print_step "Running all tests..."
            
            # Frontend tests
            cd "$FRONTEND_DIR"
            pnpm run test:ci || exit_code=$?
            pnpm run lint || exit_code=$?
            pnpm run type-check || exit_code=$?
            
            # Backend tests
            cd "$BACKEND_DIR"
            source venv/bin/activate
            python -m pytest tests/ --cov=src --cov-report=html || exit_code=$?
            python -m flake8 src/ || exit_code=$?
            python -m mypy src/ || exit_code=$?
            
            # Integration tests (if services are running)
            if curl -s http://localhost:3000 >/dev/null && curl -s http://localhost:5000 >/dev/null; then
                cd "$FRONTEND_DIR"
                pnpm run test:e2e || exit_code=$?
            else
                print_warning "Skipping integration tests - services not running"
            fi
            ;;
        *)
            print_error "Unknown test type: $test_type"
            print_status "Available types: frontend, backend, integration, all"
            exit 1
            ;;
    esac
    
    cd "$PROJECT_ROOT"
    
    if [ $exit_code -eq 0 ]; then
        print_success "All tests passed!"
    else
        print_error "Some tests failed (exit code: $exit_code)"
    fi
    
    return $exit_code
}

# Function to build project
build_project() {
    print_header "Building Project"
    cd "$PROJECT_ROOT"
    
    local build_type="${1:-all}"
    
    case "$build_type" in
        "frontend"|"fe")
            print_step "Building frontend..."
            cd "$FRONTEND_DIR"
            pnpm run build
            ;;
        "backend"|"be")
            print_step "Building backend..."
            cd "$BACKEND_DIR"
            source venv/bin/activate
            python -m py_compile src/main.py
            ;;
        "docker")
            print_step "Building Docker images..."
            docker-compose build
            ;;
        "all")
            print_step "Building frontend..."
            cd "$FRONTEND_DIR"
            pnpm run build
            
            print_step "Building backend..."
            cd "$BACKEND_DIR"
            source venv/bin/activate
            python -m py_compile src/main.py
            
            print_step "Building Docker images..."
            cd "$PROJECT_ROOT"
            docker-compose build
            ;;
        *)
            print_error "Unknown build type: $build_type"
            print_status "Available types: frontend, backend, docker, all"
            exit 1
            ;;
    esac
    
    print_success "Build completed!"
}

# Function to update dependencies
update_deps() {
    print_header "Updating Dependencies"
    cd "$PROJECT_ROOT"
    
    # Update frontend dependencies
    print_step "Updating frontend dependencies..."
    cd "$FRONTEND_DIR"
    pnpm update
    
    # Update backend dependencies
    print_step "Updating backend dependencies..."
    cd "$BACKEND_DIR"
    source venv/bin/activate
    pip install --upgrade -r requirements.txt
    pip install --upgrade -r requirements-dev.txt
    
    # Update Docker images
    print_step "Updating Docker images..."
    cd "$PROJECT_ROOT"
    docker-compose pull
    
    print_success "Dependencies updated!"
}

# Function to sync with cloud
sync_cloud() {
    print_header "Syncing with Cloud"
    cd "$PROJECT_ROOT"
    
    if [ -f "scripts/cloud-sync.sh" ]; then
        ./scripts/cloud-sync.sh "$@"
    else
        print_error "Cloud sync script not found"
        exit 1
    fi
}

# Function to deploy to environment
deploy() {
    print_header "Deploying to Environment"
    
    local environment="${1:-staging}"
    local cloud="${2:-all}"
    
    print_step "Deploying to $environment environment on $cloud..."
    
    # Run tests first
    print_step "Running tests before deployment..."
    if ! run_tests; then
        print_error "Tests failed. Deployment aborted."
        exit 1
    fi
    
    # Build project
    print_step "Building project..."
    if ! build_project; then
        print_error "Build failed. Deployment aborted."
        exit 1
    fi
    
    # Trigger deployment based on cloud provider
    case "$cloud" in
        "aws")
            print_step "Triggering AWS deployment..."
            gh workflow run deploy-aws.yml -f environment="$environment"
            ;;
        "gcp")
            print_step "Triggering GCP deployment..."
            gh workflow run deploy-gcp.yml -f environment="$environment"
            ;;
        "azure")
            print_step "Triggering Azure deployment..."
            gh workflow run deploy-azure.yml -f environment="$environment"
            ;;
        "all")
            print_step "Triggering multi-cloud deployment..."
            gh workflow run multi-cloud-deploy.yml -f environment="$environment"
            ;;
        *)
            print_error "Unknown cloud provider: $cloud"
            print_status "Available providers: aws, gcp, azure, all"
            exit 1
            ;;
    esac
    
    print_success "Deployment triggered!"
    print_status "Check GitHub Actions for deployment status"
}

# Function to reset development environment
reset_dev() {
    print_header "Resetting Development Environment"
    
    print_warning "This will:"
    echo "  - Stop all services"
    echo "  - Remove all containers and volumes"
    echo "  - Clear database data"
    echo "  - Reset environment files"
    echo
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Reset cancelled"
        return
    fi
    
    cd "$PROJECT_ROOT"
    
    # Stop everything
    stop_dev
    
    # Remove Docker containers and volumes
    docker-compose down -v --remove-orphans
    docker system prune -f
    
    # Reset environment files
    if [ -f "frontend/.env.local" ]; then
        mv "frontend/.env.local" "frontend/.env.local.backup"
        print_status "Frontend .env.local backed up"
    fi
    
    if [ -f "backend/.env" ]; then
        mv "backend/.env" "backend/.env.backup"
        print_status "Backend .env backed up"
    fi
    
    # Recreate database
    docker-compose up -d postgres redis
    sleep 10
    
    cd "$BACKEND_DIR"
    source venv/bin/activate
    python -c "
from src.database import db
from src.main import app
with app.app_context():
    db.drop_all()
    db.create_all()
    print('Database reset successfully!')
"
    
    cd "$PROJECT_ROOT"
    print_success "Development environment reset!"
    print_status "Run '$0 start' to start fresh"
}

# Function to show logs
show_logs() {
    print_header "Showing Logs"
    
    local service="${1:-all}"
    local lines="${2:-50}"
    
    case "$service" in
        "frontend"|"fe")
            if [ -f "/tmp/savelife_frontend.pid" ]; then
                print_step "Frontend logs (last $lines lines):"
                tail -n "$lines" "$FRONTEND_DIR/logs/dev.log" 2>/dev/null || echo "No frontend logs found"
            else
                print_warning "Frontend not running"
            fi
            ;;
        "backend"|"be")
            if [ -f "/tmp/savelife_backend.pid" ]; then
                print_step "Backend logs (last $lines lines):"
                tail -n "$lines" "$BACKEND_DIR/logs/app.log" 2>/dev/null || echo "No backend logs found"
            else
                print_warning "Backend not running"
            fi
            ;;
        "docker")
            print_step "Docker logs:"
            docker-compose logs --tail="$lines"
            ;;
        "all")
            show_logs "frontend" "$lines"
            echo
            show_logs "backend" "$lines"
            echo
            show_logs "docker" "$lines"
            ;;
        *)
            print_error "Unknown service: $service"
            print_status "Available services: frontend, backend, docker, all"
            exit 1
            ;;
    esac
}

# Function to open project in IDE
open_ide() {
    print_header "Opening Project in IDE"
    
    local ide="${1:-code}"
    
    case "$ide" in
        "code"|"vscode")
            if command_exists code; then
                code "$PROJECT_ROOT"
                print_success "Opened in VS Code"
            else
                print_error "VS Code not found"
            fi
            ;;
        "idea"|"intellij")
            if command_exists idea; then
                idea "$PROJECT_ROOT"
                print_success "Opened in IntelliJ IDEA"
            else
                print_error "IntelliJ IDEA not found"
            fi
            ;;
        "atom")
            if command_exists atom; then
                atom "$PROJECT_ROOT"
                print_success "Opened in Atom"
            else
                print_error "Atom not found"
            fi
            ;;
        *)
            print_error "Unknown IDE: $ide"
            print_status "Available IDEs: code, idea, atom"
            exit 1
            ;;
    esac
}

# Function to show help
show_help() {
    cat << EOF
SaveLife.com Development Workflow Script

Usage: $0 <command> [options]

Commands:
  start                 Start development environment
  stop                  Stop development environment
  restart               Restart development environment
  status                Show environment status
  
  test [type]           Run tests (frontend|backend|integration|all)
  build [type]          Build project (frontend|backend|docker|all)
  
  update                Update all dependencies
  sync [options]        Sync with cloud resources
  deploy [env] [cloud]  Deploy to environment (staging|prod) on cloud (aws|gcp|azure|all)
  
  reset                 Reset development environment
  logs [service] [lines] Show logs (frontend|backend|docker|all)
  ide [editor]          Open project in IDE (code|idea|atom)
  
  help                  Show this help message

Examples:
  $0 start              # Start development environment
  $0 test frontend      # Run frontend tests only
  $0 build docker       # Build Docker images
  $0 deploy staging aws # Deploy to staging on AWS
  $0 logs backend 100   # Show last 100 backend log lines
  $0 sync --env         # Sync environment variables from cloud

Environment Variables:
  SAVELIFE_ENV         Development environment (default: development)
  SAVELIFE_DEBUG       Enable debug mode (default: true)

EOF
}

# Main function
main() {
    local command="${1:-help}"
    shift || true
    
    case "$command" in
        "start")
            start_dev
            ;;
        "stop")
            stop_dev
            ;;
        "restart")
            restart_dev
            ;;
        "status")
            status_dev
            ;;
        "test")
            run_tests "$@"
            ;;
        "build")
            build_project "$@"
            ;;
        "update")
            update_deps
            ;;
        "sync")
            sync_cloud "$@"
            ;;
        "deploy")
            deploy "$@"
            ;;
        "reset")
            reset_dev
            ;;
        "logs")
            show_logs "$@"
            ;;
        "ide")
            open_ide "$@"
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        *)
            print_error "Unknown command: $command"
            echo
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"

