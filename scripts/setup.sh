#!/bin/bash

# PlaybookWiz Setup Script
# This script sets up the development environment for the Brand Playbook Intelligence App

set -e  # Exit on any error

echo "🚀 Setting up PlaybookWiz - Brand Playbook Intelligence App"
echo "============================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Node.js
    if command_exists node; then
        NODE_VERSION=$(node --version)
        print_success "Node.js found: $NODE_VERSION"
    else
        print_error "Node.js is not installed. Please install Node.js 18+ from https://nodejs.org/"
        exit 1
    fi
    
    # Check npm
    if command_exists npm; then
        NPM_VERSION=$(npm --version)
        print_success "npm found: $NPM_VERSION"
    else
        print_error "npm is not installed. Please install npm."
        exit 1
    fi
    
    # Check Python
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version)
        print_success "Python found: $PYTHON_VERSION"
    else
        print_error "Python 3.11+ is not installed. Please install Python from https://python.org/"
        exit 1
    fi
    
    # Check pip
    if command_exists pip3; then
        PIP_VERSION=$(pip3 --version)
        print_success "pip found: $PIP_VERSION"
    else
        print_error "pip is not installed. Please install pip."
        exit 1
    fi
    
    # Check Docker (optional)
    if command_exists docker; then
        DOCKER_VERSION=$(docker --version)
        print_success "Docker found: $DOCKER_VERSION"
    else
        print_warning "Docker not found. You can install it later for containerized deployment."
    fi
    
    # Check Docker Compose (optional)
    if command_exists docker-compose; then
        DOCKER_COMPOSE_VERSION=$(docker-compose --version)
        print_success "Docker Compose found: $DOCKER_COMPOSE_VERSION"
    else
        print_warning "Docker Compose not found. You can install it later for containerized deployment."
    fi
}

# Setup environment files
setup_environment() {
    print_status "Setting up environment files..."
    
    # Copy environment files if they don't exist
    if [ ! -f .env.local ]; then
        cp .env.example .env.local
        print_success "Created .env.local from .env.example"
        print_warning "Please update .env.local with your actual configuration values"
    else
        print_warning ".env.local already exists, skipping..."
    fi
    
    if [ ! -f backend/.env ]; then
        cp backend/.env.example backend/.env
        print_success "Created backend/.env from backend/.env.example"
        print_warning "Please update backend/.env with your actual configuration values"
    else
        print_warning "backend/.env already exists, skipping..."
    fi
}

# Install frontend dependencies
setup_frontend() {
    print_status "Setting up frontend dependencies..."
    
    if [ -d "frontend" ]; then
        cd frontend
        
        # Install dependencies
        print_status "Installing frontend dependencies..."
        npm install
        
        print_success "Frontend dependencies installed successfully"
        cd ..
    else
        print_error "Frontend directory not found"
        exit 1
    fi
}

# Install backend dependencies
setup_backend() {
    print_status "Setting up backend dependencies..."
    
    if [ -d "backend" ]; then
        cd backend
        
        # Create virtual environment if it doesn't exist
        if [ ! -d "venv" ]; then
            print_status "Creating Python virtual environment..."
            python3 -m venv venv
            print_success "Virtual environment created"
        fi
        
        # Activate virtual environment
        print_status "Activating virtual environment..."
        source venv/bin/activate
        
        # Upgrade pip
        print_status "Upgrading pip..."
        pip install --upgrade pip
        
        # Install dependencies
        print_status "Installing backend dependencies..."
        pip install -r requirements.txt
        
        print_success "Backend dependencies installed successfully"
        
        # Deactivate virtual environment
        deactivate
        cd ..
    else
        print_error "Backend directory not found"
        exit 1
    fi
}

# Setup databases with Docker
setup_databases() {
    print_status "Setting up databases..."
    
    if command_exists docker && command_exists docker-compose; then
        print_status "Starting databases with Docker Compose..."
        docker-compose up -d postgres mongodb redis
        
        # Wait for databases to be ready
        print_status "Waiting for databases to be ready..."
        sleep 10
        
        print_success "Databases started successfully"
    else
        print_warning "Docker not available. Please set up PostgreSQL, MongoDB, and Redis manually."
        print_warning "PostgreSQL: https://postgresql.org/download/"
        print_warning "MongoDB: https://docs.mongodb.com/manual/installation/"
        print_warning "Redis: https://redis.io/download"
    fi
}

# Run database migrations
setup_database_schema() {
    print_status "Setting up database schema..."
    
    cd backend
    source venv/bin/activate
    
    # Initialize Alembic if not already done
    if [ ! -d "alembic" ]; then
        print_status "Initializing Alembic..."
        alembic init alembic
    fi
    
    # Run migrations
    print_status "Running database migrations..."
    alembic upgrade head
    
    print_success "Database schema setup completed"
    
    deactivate
    cd ..
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    # Create upload directory
    mkdir -p backend/uploads
    
    # Create logs directory
    mkdir -p logs
    
    # Create test directories
    mkdir -p tests/frontend
    mkdir -p tests/backend
    
    print_success "Directories created successfully"
}

# Display next steps
show_next_steps() {
    echo ""
    echo "🎉 Setup completed successfully!"
    echo "================================"
    echo ""
    echo "Next steps:"
    echo "1. Update environment variables in .env.local and backend/.env"
    echo "2. Add your Anthropic API key to backend/.env:"
    echo "   ANTHROPIC_API_KEY=your-api-key-here"
    echo "3. Add your OpenAI API key for embeddings (optional):"
    echo "   OPENAI_API_KEY=your-api-key-here"
    echo "4. Configure your database URLs if not using Docker"
    echo ""
    echo "To start the development servers:"
    echo "  npm run dev                    # Start both frontend and backend"
    echo "  npm run dev:frontend          # Start only frontend"
    echo "  npm run dev:backend           # Start only backend"
    echo ""
    echo "To run with Docker:"
    echo "  docker-compose up --build     # Start all services"
    echo ""
    echo "Access the application:"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend API: http://localhost:8000"
    echo "  API Documentation: http://localhost:8000/docs"
    echo ""
    echo "For more information, see README.md"
}

# Main setup function
main() {
    check_prerequisites
    setup_environment
    create_directories
    setup_frontend
    setup_backend
    setup_databases
    # setup_database_schema  # Commented out as it requires proper DB connection
    show_next_steps
}

# Run main function
main
