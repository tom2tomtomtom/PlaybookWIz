#!/bin/bash

# Production Validation Script for PlaybookWiz
# This script validates that the production deployment is working correctly

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3000}"
TIMEOUT=10

# Counters
TESTS_PASSED=0
TESTS_FAILED=0

# Functions
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((TESTS_PASSED++))
}

print_failure() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((TESTS_FAILED++))
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Test functions
test_backend_health() {
    print_status "Testing backend health endpoint..."
    
    if curl -f -s --max-time $TIMEOUT "$BACKEND_URL/health" > /dev/null; then
        print_success "Backend health check passed"
    else
        print_failure "Backend health check failed"
    fi
}

test_backend_detailed_health() {
    print_status "Testing backend detailed health endpoint..."
    
    local response
    response=$(curl -f -s --max-time $TIMEOUT "$BACKEND_URL/api/v1/health/detailed" 2>/dev/null || echo "")
    
    if [ -n "$response" ]; then
        local status
        status=$(echo "$response" | grep -o '"status":"[^"]*"' | cut -d'"' -f4 || echo "")
        
        if [ "$status" = "healthy" ] || [ "$status" = "degraded" ]; then
            print_success "Backend detailed health check passed (status: $status)"
        else
            print_failure "Backend detailed health check failed (status: $status)"
        fi
    else
        print_failure "Backend detailed health check failed (no response)"
    fi
}

test_backend_readiness() {
    print_status "Testing backend readiness probe..."
    
    if curl -f -s --max-time $TIMEOUT "$BACKEND_URL/api/v1/health/readiness" > /dev/null; then
        print_success "Backend readiness probe passed"
    else
        print_failure "Backend readiness probe failed"
    fi
}

test_backend_liveness() {
    print_status "Testing backend liveness probe..."
    
    if curl -f -s --max-time $TIMEOUT "$BACKEND_URL/api/v1/health/liveness" > /dev/null; then
        print_success "Backend liveness probe passed"
    else
        print_failure "Backend liveness probe failed"
    fi
}

test_frontend_health() {
    print_status "Testing frontend health endpoint..."
    
    if curl -f -s --max-time $TIMEOUT "$FRONTEND_URL/api/health" > /dev/null; then
        print_success "Frontend health check passed"
    else
        print_failure "Frontend health check failed"
    fi
}

test_frontend_accessibility() {
    print_status "Testing frontend accessibility..."
    
    if curl -f -s --max-time $TIMEOUT "$FRONTEND_URL" > /dev/null; then
        print_success "Frontend is accessible"
    else
        print_failure "Frontend is not accessible"
    fi
}

test_api_docs() {
    print_status "Testing API documentation..."
    
    if curl -f -s --max-time $TIMEOUT "$BACKEND_URL/docs" > /dev/null; then
        print_success "API documentation is accessible"
    else
        print_failure "API documentation is not accessible"
    fi
}

test_cors_headers() {
    print_status "Testing CORS headers..."
    
    local response
    response=$(curl -s -I --max-time $TIMEOUT -H "Origin: $FRONTEND_URL" "$BACKEND_URL/health" 2>/dev/null || echo "")
    
    if echo "$response" | grep -i "access-control-allow-origin" > /dev/null; then
        print_success "CORS headers are present"
    else
        print_warning "CORS headers not found (may be intentional for production)"
    fi
}

test_security_headers() {
    print_status "Testing security headers..."
    
    local response
    response=$(curl -s -I --max-time $TIMEOUT "$FRONTEND_URL" 2>/dev/null || echo "")
    
    local security_headers=("x-frame-options" "x-content-type-options" "x-xss-protection")
    local headers_found=0
    
    for header in "${security_headers[@]}"; do
        if echo "$response" | grep -i "$header" > /dev/null; then
            ((headers_found++))
        fi
    done
    
    if [ $headers_found -gt 0 ]; then
        print_success "Security headers found ($headers_found/3)"
    else
        print_warning "No security headers found"
    fi
}

test_response_times() {
    print_status "Testing response times..."
    
    local backend_time
    backend_time=$(curl -o /dev/null -s -w "%{time_total}" --max-time $TIMEOUT "$BACKEND_URL/health" 2>/dev/null || echo "999")
    
    if (( $(echo "$backend_time < 2.0" | bc -l) )); then
        print_success "Backend response time: ${backend_time}s"
    else
        print_failure "Backend response time too slow: ${backend_time}s"
    fi
    
    local frontend_time
    frontend_time=$(curl -o /dev/null -s -w "%{time_total}" --max-time $TIMEOUT "$FRONTEND_URL" 2>/dev/null || echo "999")
    
    if (( $(echo "$frontend_time < 3.0" | bc -l) )); then
        print_success "Frontend response time: ${frontend_time}s"
    else
        print_failure "Frontend response time too slow: ${frontend_time}s"
    fi
}

test_database_connectivity() {
    print_status "Testing database connectivity through health endpoint..."
    
    local response
    response=$(curl -f -s --max-time $TIMEOUT "$BACKEND_URL/api/v1/health/detailed" 2>/dev/null || echo "")
    
    if echo "$response" | grep -q '"postgres":{"status":"healthy"'; then
        print_success "PostgreSQL connectivity confirmed"
    else
        print_failure "PostgreSQL connectivity issue detected"
    fi
    
    if echo "$response" | grep -q '"redis":{"status":"healthy"'; then
        print_success "Redis connectivity confirmed"
    else
        print_failure "Redis connectivity issue detected"
    fi
    
    if echo "$response" | grep -q '"mongodb":{"status":"healthy"'; then
        print_success "MongoDB connectivity confirmed"
    else
        print_warning "MongoDB connectivity issue (may be non-critical)"
    fi
}

# Main execution
main() {
    print_status "Starting PlaybookWiz production validation..."
    print_status "Backend URL: $BACKEND_URL"
    print_status "Frontend URL: $FRONTEND_URL"
    echo ""
    
    # Run all tests
    test_backend_health
    test_backend_detailed_health
    test_backend_readiness
    test_backend_liveness
    test_frontend_health
    test_frontend_accessibility
    test_api_docs
    test_cors_headers
    test_security_headers
    test_response_times
    test_database_connectivity
    
    echo ""
    print_status "Validation Summary:"
    print_success "Tests passed: $TESTS_PASSED"
    
    if [ $TESTS_FAILED -gt 0 ]; then
        print_failure "Tests failed: $TESTS_FAILED"
        echo ""
        print_failure "Production validation failed! Please review the failed tests above."
        exit 1
    else
        echo ""
        print_success "All tests passed! Production deployment appears to be working correctly."
        exit 0
    fi
}

# Check if bc is available for floating point comparison
if ! command -v bc &> /dev/null; then
    print_warning "bc command not found, skipping response time validation"
    test_response_times() {
        print_warning "Skipping response time tests (bc not available)"
    }
fi

# Parse command line arguments
case "${1:-validate}" in
    "validate")
        main
        ;;
    "backend")
        test_backend_health
        test_backend_detailed_health
        test_backend_readiness
        test_backend_liveness
        test_database_connectivity
        ;;
    "frontend")
        test_frontend_health
        test_frontend_accessibility
        ;;
    "performance")
        test_response_times
        ;;
    *)
        echo "Usage: $0 {validate|backend|frontend|performance}"
        exit 1
        ;;
esac
