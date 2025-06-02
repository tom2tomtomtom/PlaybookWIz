#!/bin/bash

# Production Deployment Script for PlaybookWiz
# This script handles production deployment with proper checks and rollback capabilities

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.prod"
BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"

# Functions
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

check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if Docker is installed and running
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker is not running"
        exit 1
    fi
    
    # Check if Docker Compose is available
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not available"
        exit 1
    fi
    
    # Check if production environment file exists
    if [ ! -f "$ENV_FILE" ]; then
        print_error "Production environment file $ENV_FILE not found"
        print_status "Please copy .env.production to $ENV_FILE and configure it"
        exit 1
    fi
    
    # Check if production compose file exists
    if [ ! -f "$COMPOSE_FILE" ]; then
        print_error "Production compose file $COMPOSE_FILE not found"
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

validate_environment() {
    print_status "Validating environment configuration..."
    
    # Source the environment file
    set -a
    source "$ENV_FILE"
    set +a
    
    # Check required variables
    required_vars=(
        "POSTGRES_PASSWORD"
        "MONGO_PASSWORD"
        "SECRET_KEY"
        "ANTHROPIC_API_KEY"
    )
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var:-}" ]; then
            print_error "Required environment variable $var is not set"
            exit 1
        fi
    done
    
    # Check if secrets are not default values
    if [ "$POSTGRES_PASSWORD" = "your-secure-postgres-password-here" ]; then
        print_error "Please update POSTGRES_PASSWORD in $ENV_FILE"
        exit 1
    fi
    
    if [ "$SECRET_KEY" = "your-super-secret-key-here-min-32-chars" ]; then
        print_error "Please update SECRET_KEY in $ENV_FILE"
        exit 1
    fi
    
    print_success "Environment validation passed"
}

backup_data() {
    print_status "Creating backup..."
    
    mkdir -p "$BACKUP_DIR"
    
    # Backup database if containers are running
    if docker-compose -f "$COMPOSE_FILE" ps postgres | grep -q "Up"; then
        print_status "Backing up PostgreSQL database..."
        docker-compose -f "$COMPOSE_FILE" exec -T postgres pg_dump -U playbookwiz playbookwiz > "$BACKUP_DIR/postgres_backup.sql"
    fi
    
    if docker-compose -f "$COMPOSE_FILE" ps mongodb | grep -q "Up"; then
        print_status "Backing up MongoDB database..."
        docker-compose -f "$COMPOSE_FILE" exec -T mongodb mongodump --archive > "$BACKUP_DIR/mongodb_backup.archive"
    fi
    
    # Backup uploads directory
    if [ -d "./uploads" ]; then
        print_status "Backing up uploads directory..."
        cp -r ./uploads "$BACKUP_DIR/"
    fi
    
    print_success "Backup created at $BACKUP_DIR"
}

deploy() {
    print_status "Starting production deployment..."
    
    # Pull latest images
    print_status "Pulling latest images..."
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" pull
    
    # Build images
    print_status "Building application images..."
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" build --no-cache
    
    # Start services
    print_status "Starting services..."
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d
    
    # Wait for services to be healthy
    print_status "Waiting for services to be healthy..."
    sleep 30
    
    # Check health
    check_health
}

check_health() {
    print_status "Checking service health..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        print_status "Health check attempt $attempt/$max_attempts"
        
        # Check backend health
        if curl -f -s http://localhost:8000/health > /dev/null; then
            print_success "Backend is healthy"
            break
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            print_error "Backend health check failed after $max_attempts attempts"
            return 1
        fi
        
        sleep 10
        ((attempt++))
    done
    
    # Check frontend health
    if curl -f -s http://localhost:3000/api/health > /dev/null; then
        print_success "Frontend is healthy"
    else
        print_warning "Frontend health check failed, but continuing..."
    fi
    
    print_success "Health checks completed"
}

rollback() {
    print_error "Deployment failed, initiating rollback..."
    
    # Stop current containers
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" down
    
    # Restore from backup if available
    if [ -d "$BACKUP_DIR" ]; then
        print_status "Restoring from backup..."
        
        # Restore database
        if [ -f "$BACKUP_DIR/postgres_backup.sql" ]; then
            print_status "Restoring PostgreSQL database..."
            docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d postgres
            sleep 10
            docker-compose -f "$COMPOSE_FILE" exec -T postgres psql -U playbookwiz -d playbookwiz < "$BACKUP_DIR/postgres_backup.sql"
        fi
        
        # Restore uploads
        if [ -d "$BACKUP_DIR/uploads" ]; then
            print_status "Restoring uploads directory..."
            rm -rf ./uploads
            cp -r "$BACKUP_DIR/uploads" ./
        fi
    fi
    
    print_error "Rollback completed"
    exit 1
}

cleanup() {
    print_status "Cleaning up old images and containers..."
    
    # Remove unused images
    docker image prune -f
    
    # Remove old backups (keep last 5)
    if [ -d "./backups" ]; then
        ls -t ./backups | tail -n +6 | xargs -r -I {} rm -rf "./backups/{}"
    fi
    
    print_success "Cleanup completed"
}

show_status() {
    print_status "Deployment Status:"
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps
    
    print_status "Service URLs:"
    echo "Frontend: http://localhost:3000"
    echo "Backend API: http://localhost:8000"
    echo "API Documentation: http://localhost:8000/docs"
}

# Main execution
main() {
    print_status "Starting PlaybookWiz production deployment..."
    
    # Trap errors and rollback
    trap rollback ERR
    
    check_prerequisites
    validate_environment
    backup_data
    deploy
    cleanup
    show_status
    
    print_success "Production deployment completed successfully!"
    print_status "Monitor the logs with: docker-compose -f $COMPOSE_FILE logs -f"
}

# Parse command line arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "rollback")
        rollback
        ;;
    "status")
        show_status
        ;;
    "health")
        check_health
        ;;
    *)
        echo "Usage: $0 {deploy|rollback|status|health}"
        exit 1
        ;;
esac
