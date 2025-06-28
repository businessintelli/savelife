#!/bin/bash

# SaveLife.com Local Development Setup Script
# This script sets up a complete local development environment for SaveLife.com

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="SaveLife.com"
REPO_URL="https://github.com/$(git config user.name)/savelife.git"
LOCAL_DIR="$HOME/savelife-dev"
DOCKER_COMPOSE_VERSION="2.20.0"
NODE_VERSION="18"
PYTHON_VERSION="3.11"

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

# Function to get OS information
get_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

# Function to install dependencies based on OS
install_dependencies() {
    local os=$(get_os)
    print_step "Installing dependencies for $os..."
    
    case $os in
        "linux")
            # Update package list
            sudo apt-get update
            
            # Install basic dependencies
            sudo apt-get install -y \
                curl \
                wget \
                git \
                unzip \
                software-properties-common \
                apt-transport-https \
                ca-certificates \
                gnupg \
                lsb-release
            ;;
        "macos")
            # Check if Homebrew is installed
            if ! command_exists brew; then
                print_status "Installing Homebrew..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            fi
            
            # Update Homebrew
            brew update
            ;;
        "windows")
            print_warning "Windows detected. Please ensure you have Git Bash or WSL installed."
            print_warning "Some features may require manual installation."
            ;;
        *)
            print_error "Unsupported operating system: $os"
            exit 1
            ;;
    esac
}

# Function to install Docker
install_docker() {
    print_step "Installing Docker..."
    local os=$(get_os)
    
    if command_exists docker; then
        print_status "Docker is already installed."
        return
    fi
    
    case $os in
        "linux")
            # Install Docker
            curl -fsSL https://get.docker.com -o get-docker.sh
            sudo sh get-docker.sh
            rm get-docker.sh
            
            # Add user to docker group
            sudo usermod -aG docker $USER
            
            # Install Docker Compose
            sudo curl -L "https://github.com/docker/compose/releases/download/v${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
            sudo chmod +x /usr/local/bin/docker-compose
            ;;
        "macos")
            print_status "Please install Docker Desktop for Mac from https://www.docker.com/products/docker-desktop"
            print_warning "After installation, restart this script."
            exit 1
            ;;
        "windows")
            print_status "Please install Docker Desktop for Windows from https://www.docker.com/products/docker-desktop"
            print_warning "After installation, restart this script."
            exit 1
            ;;
    esac
}

# Function to install Node.js
install_nodejs() {
    print_step "Installing Node.js..."
    
    if command_exists node; then
        local current_version=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
        if [ "$current_version" -ge "$NODE_VERSION" ]; then
            print_status "Node.js $NODE_VERSION+ is already installed."
            return
        fi
    fi
    
    local os=$(get_os)
    case $os in
        "linux")
            # Install Node.js via NodeSource repository
            curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | sudo -E bash -
            sudo apt-get install -y nodejs
            ;;
        "macos")
            brew install node@${NODE_VERSION}
            ;;
        "windows")
            print_status "Please install Node.js from https://nodejs.org/"
            print_warning "After installation, restart this script."
            exit 1
            ;;
    esac
    
    # Install global packages
    npm install -g pnpm yarn
}

# Function to install Python
install_python() {
    print_step "Installing Python..."
    
    if command_exists python3; then
        local current_version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
        if [ "$current_version" = "$PYTHON_VERSION" ]; then
            print_status "Python $PYTHON_VERSION is already installed."
            return
        fi
    fi
    
    local os=$(get_os)
    case $os in
        "linux")
            sudo apt-get install -y python${PYTHON_VERSION} python${PYTHON_VERSION}-pip python${PYTHON_VERSION}-venv
            ;;
        "macos")
            brew install python@${PYTHON_VERSION}
            ;;
        "windows")
            print_status "Please install Python from https://www.python.org/"
            print_warning "After installation, restart this script."
            exit 1
            ;;
    esac
    
    # Install pipenv and poetry
    pip3 install pipenv poetry
}

# Function to install cloud CLIs
install_cloud_clis() {
    print_step "Installing cloud CLIs..."
    local os=$(get_os)
    
    # Install AWS CLI
    if ! command_exists aws; then
        print_status "Installing AWS CLI..."
        case $os in
            "linux")
                curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
                unzip awscliv2.zip
                sudo ./aws/install
                rm -rf aws awscliv2.zip
                ;;
            "macos")
                brew install awscli
                ;;
        esac
    fi
    
    # Install Google Cloud CLI
    if ! command_exists gcloud; then
        print_status "Installing Google Cloud CLI..."
        case $os in
            "linux")
                echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
                curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -
                sudo apt-get update && sudo apt-get install -y google-cloud-cli
                ;;
            "macos")
                brew install google-cloud-sdk
                ;;
        esac
    fi
    
    # Install Azure CLI
    if ! command_exists az; then
        print_status "Installing Azure CLI..."
        case $os in
            "linux")
                curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
                ;;
            "macos")
                brew install azure-cli
                ;;
        esac
    fi
}

# Function to install development tools
install_dev_tools() {
    print_step "Installing development tools..."
    local os=$(get_os)
    
    case $os in
        "linux")
            sudo apt-get install -y \
                vim \
                nano \
                htop \
                tree \
                jq \
                postgresql-client \
                redis-tools
            ;;
        "macos")
            brew install \
                vim \
                htop \
                tree \
                jq \
                postgresql \
                redis
            ;;
    esac
    
    # Install VS Code extensions helper
    if command_exists code; then
        print_status "Installing VS Code extensions..."
        code --install-extension ms-python.python
        code --install-extension ms-vscode.vscode-typescript-next
        code --install-extension bradlc.vscode-tailwindcss
        code --install-extension ms-vscode.vscode-docker
        code --install-extension ms-azuretools.vscode-docker
        code --install-extension googlecloudtools.cloudcode
        code --install-extension amazonwebservices.aws-toolkit-vscode
    fi
}

# Function to clone repository
clone_repository() {
    print_step "Setting up project repository..."
    
    if [ -d "$LOCAL_DIR" ]; then
        print_warning "Directory $LOCAL_DIR already exists."
        read -p "Do you want to remove it and clone fresh? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$LOCAL_DIR"
        else
            print_status "Using existing directory."
            cd "$LOCAL_DIR"
            git pull origin main
            return
        fi
    fi
    
    # Clone repository
    git clone "$REPO_URL" "$LOCAL_DIR"
    cd "$LOCAL_DIR"
    
    # Set up git hooks
    print_status "Setting up git hooks..."
    cp scripts/git-hooks/* .git/hooks/
    chmod +x .git/hooks/*
}

# Function to set up environment files
setup_environment() {
    print_step "Setting up environment configuration..."
    cd "$LOCAL_DIR"
    
    # Create frontend environment file
    if [ ! -f "frontend/.env.local" ]; then
        cat > frontend/.env.local << EOF
# SaveLife.com Frontend Environment Configuration
REACT_APP_API_URL=http://localhost:5000
REACT_APP_ENVIRONMENT=development
REACT_APP_STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_key_here
REACT_APP_GOOGLE_ANALYTICS_ID=GA_MEASUREMENT_ID
REACT_APP_SENTRY_DSN=your_sentry_dsn_here
EOF
        print_status "Created frontend/.env.local"
    fi
    
    # Create backend environment file
    if [ ! -f "backend/.env" ]; then
        cat > backend/.env << EOF
# SaveLife.com Backend Environment Configuration
FLASK_ENV=development
FLASK_DEBUG=True
DATABASE_URL=postgresql://savelife:password@localhost:5432/savelife_dev
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=your_openai_api_key_here
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key_here
JWT_SECRET=your_jwt_secret_here
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
UPLOAD_FOLDER=./uploads
MAX_CONTENT_LENGTH=16777216
EOF
        print_status "Created backend/.env"
    fi
    
    # Create docker-compose override for development
    if [ ! -f "docker-compose.override.yml" ]; then
        cat > docker-compose.override.yml << EOF
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      target: development
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - CHOKIDAR_USEPOLLING=true
    ports:
      - "3000:3000"
    command: pnpm run dev

  backend:
    build:
      context: ./backend
      target: development
    volumes:
      - ./backend:/app
    environment:
      - FLASK_ENV=development
      - FLASK_DEBUG=True
    ports:
      - "5000:5000"
    command: python src/main.py

  postgres:
    environment:
      - POSTGRES_DB=savelife_dev
      - POSTGRES_USER=savelife
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - postgres_dev_data:/var/lib/postgresql/data

  redis:
    ports:
      - "6379:6379"
    volumes:
      - redis_dev_data:/data

volumes:
  postgres_dev_data:
  redis_dev_data:
EOF
        print_status "Created docker-compose.override.yml"
    fi
}

# Function to install project dependencies
install_project_dependencies() {
    print_step "Installing project dependencies..."
    cd "$LOCAL_DIR"
    
    # Install frontend dependencies
    print_status "Installing frontend dependencies..."
    cd frontend
    pnpm install
    cd ..
    
    # Install backend dependencies
    print_status "Installing backend dependencies..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    cd ..
}

# Function to set up database
setup_database() {
    print_step "Setting up development database..."
    cd "$LOCAL_DIR"
    
    # Start database services
    docker-compose up -d postgres redis
    
    # Wait for database to be ready
    print_status "Waiting for database to be ready..."
    sleep 10
    
    # Run database migrations
    cd backend
    source venv/bin/activate
    python -c "
from src.database import db
from src.main import app
with app.app_context():
    db.create_all()
    print('Database tables created successfully!')
"
    cd ..
}

# Function to create development scripts
create_dev_scripts() {
    print_step "Creating development scripts..."
    cd "$LOCAL_DIR"
    
    # Create start script
    cat > scripts/start-dev.sh << 'EOF'
#!/bin/bash
# Start SaveLife.com development environment

echo "Starting SaveLife.com development environment..."

# Start infrastructure services
docker-compose up -d postgres redis

# Wait for services to be ready
sleep 5

# Start backend in background
cd backend
source venv/bin/activate
python src/main.py &
BACKEND_PID=$!
cd ..

# Start frontend
cd frontend
pnpm run dev &
FRONTEND_PID=$!
cd ..

echo "Development environment started!"
echo "Frontend: http://localhost:3000"
echo "Backend: http://localhost:5000"
echo "Database: postgresql://savelife:password@localhost:5432/savelife_dev"
echo "Redis: redis://localhost:6379/0"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap "kill $BACKEND_PID $FRONTEND_PID; docker-compose down; exit" INT
wait
EOF
    
    # Create stop script
    cat > scripts/stop-dev.sh << 'EOF'
#!/bin/bash
# Stop SaveLife.com development environment

echo "Stopping SaveLife.com development environment..."

# Kill Node.js and Python processes
pkill -f "pnpm run dev"
pkill -f "python src/main.py"

# Stop Docker services
docker-compose down

echo "Development environment stopped!"
EOF
    
    # Create test script
    cat > scripts/run-tests.sh << 'EOF'
#!/bin/bash
# Run all tests for SaveLife.com

echo "Running SaveLife.com test suite..."

# Run frontend tests
echo "Running frontend tests..."
cd frontend
pnpm run test:ci
pnpm run lint
pnpm run type-check
cd ..

# Run backend tests
echo "Running backend tests..."
cd backend
source venv/bin/activate
python -m pytest tests/ --cov=src --cov-report=html
python -m flake8 src/
python -m mypy src/
cd ..

echo "All tests completed!"
EOF
    
    # Create sync script
    cat > scripts/sync-with-cloud.sh << 'EOF'
#!/bin/bash
# Sync local development with cloud resources

echo "Syncing with cloud resources..."

# Pull latest from repository
git pull origin main

# Update dependencies
cd frontend && pnpm install && cd ..
cd backend && source venv/bin/activate && pip install -r requirements.txt && cd ..

# Sync environment variables from cloud
echo "Syncing environment variables..."
# Add cloud sync logic here

echo "Sync completed!"
EOF
    
    # Make scripts executable
    chmod +x scripts/*.sh
    
    print_status "Development scripts created in scripts/ directory"
}

# Function to configure IDE settings
configure_ide() {
    print_step "Configuring IDE settings..."
    cd "$LOCAL_DIR"
    
    # Create VS Code workspace settings
    mkdir -p .vscode
    cat > .vscode/settings.json << EOF
{
    "python.defaultInterpreterPath": "./backend/venv/bin/python",
    "python.terminal.activateEnvironment": true,
    "typescript.preferences.importModuleSpecifier": "relative",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.fixAll.eslint": true
    },
    "files.exclude": {
        "**/node_modules": true,
        "**/__pycache__": true,
        "**/venv": true,
        "**/.pytest_cache": true
    },
    "docker.defaultRegistryPath": "savelifeprod.azurecr.io",
    "aws.profile": "savelife-dev",
    "gcp.project": "savelife-platform"
}
EOF
    
    # Create launch configuration
    cat > .vscode/launch.json << EOF
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Flask",
            "type": "python",
            "request": "launch",
            "program": "\${workspaceFolder}/backend/src/main.py",
            "env": {
                "FLASK_ENV": "development",
                "FLASK_DEBUG": "True"
            },
            "args": [],
            "jinja": true,
            "justMyCode": true
        },
        {
            "name": "Debug React App",
            "type": "node",
            "request": "launch",
            "cwd": "\${workspaceFolder}/frontend",
            "runtimeExecutable": "pnpm",
            "runtimeArgs": ["run", "dev"]
        }
    ]
}
EOF
    
    # Create tasks configuration
    cat > .vscode/tasks.json << EOF
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Start Development Environment",
            "type": "shell",
            "command": "./scripts/start-dev.sh",
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            }
        },
        {
            "label": "Run Tests",
            "type": "shell",
            "command": "./scripts/run-tests.sh",
            "group": "test",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            }
        },
        {
            "label": "Build Docker Images",
            "type": "shell",
            "command": "docker-compose build",
            "group": "build"
        }
    ]
}
EOF
    
    print_status "VS Code configuration created"
}

# Function to display completion message
display_completion() {
    print_step "Setup completed successfully!"
    echo
    echo "=== SaveLife.com Development Environment ==="
    echo "Project directory: $LOCAL_DIR"
    echo "Frontend: http://localhost:3000"
    echo "Backend: http://localhost:5000"
    echo "Database: postgresql://savelife:password@localhost:5432/savelife_dev"
    echo "Redis: redis://localhost:6379/0"
    echo
    echo "=== Quick Start Commands ==="
    echo "Start development: ./scripts/start-dev.sh"
    echo "Stop development: ./scripts/stop-dev.sh"
    echo "Run tests: ./scripts/run-tests.sh"
    echo "Sync with cloud: ./scripts/sync-with-cloud.sh"
    echo
    echo "=== Next Steps ==="
    echo "1. Configure your cloud credentials:"
    echo "   - AWS: aws configure"
    echo "   - GCP: gcloud auth login"
    echo "   - Azure: az login"
    echo "2. Update environment variables in .env files"
    echo "3. Start development: cd $LOCAL_DIR && ./scripts/start-dev.sh"
    echo
    print_status "Happy coding! 🚀"
}

# Main function
main() {
    echo "=== SaveLife.com Local Development Setup ==="
    echo "This script will set up a complete development environment for $PROJECT_NAME"
    echo
    
    # Check if running as root
    if [ "$EUID" -eq 0 ]; then
        print_error "Please do not run this script as root"
        exit 1
    fi
    
    # Confirm before proceeding
    read -p "Do you want to continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Setup cancelled."
        exit 0
    fi
    
    # Run setup steps
    install_dependencies
    install_docker
    install_nodejs
    install_python
    install_cloud_clis
    install_dev_tools
    clone_repository
    setup_environment
    install_project_dependencies
    setup_database
    create_dev_scripts
    configure_ide
    display_completion
}

# Run main function
main "$@"

