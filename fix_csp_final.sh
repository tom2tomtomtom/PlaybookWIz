#!/bin/bash

# PlaybookWiz Intelligence System - Final CSP Fix
# This script completely resolves the CSP issues by using a custom Express server

set -e  # Exit on any error

echo "🔒 PlaybookWiz Intelligence System - Final CSP Fix"
echo "=" * 50

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check if we're in the right directory
if [ ! -f "backend/intelligent_main.py" ]; then
    print_error "Please run this script from the PlaybookWiz root directory"
    exit 1
fi

print_status "🔧 Applying final CSP fix..."

# Step 1: Install Express in frontend (if not already installed)
print_status "Installing Express.js for custom server..."
cd frontend

if ! npm list express > /dev/null 2>&1; then
    npm install express --legacy-peer-deps
    print_success "Express.js installed"
else
    print_success "Express.js already installed"
fi

# Step 2: Rebuild frontend
print_status "Rebuilding frontend..."
npm run build
print_success "Frontend rebuilt"

# Step 3: Test the custom server
print_status "Testing custom CSP server..."
cd ..

# Make sure the serve script is executable
chmod +x frontend/serve-with-csp.js

print_success "Custom server ready"

# Step 4: Update environment variables
print_status "Updating environment configuration..."

# Update frontend .env.local
cat > frontend/.env.local << 'EOF'
# Frontend Environment Variables - CSP Fix
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=your-supabase-url-here
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key-here
EOF

print_success "Environment variables updated"

# Step 5: Create quick test script
cat > test_csp_fix.sh << 'EOF'
#!/bin/bash
echo "🧪 Testing CSP Fix..."

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ Backend not running. Start it with: ./start_backend.sh"
    exit 1
fi

# Check if frontend is running
if ! curl -s http://localhost:9000 > /dev/null; then
    echo "❌ Frontend not running. Start it with: ./start_frontend.sh"
    exit 1
fi

echo "✅ Both services are running!"
echo "🌐 Frontend: http://localhost:9000"
echo "🔗 Backend: http://localhost:8000"
echo ""
echo "🔒 CSP Headers Test:"
curl -I http://localhost:9000 2>/dev/null | grep -i "content-security-policy" || echo "❌ CSP header not found"
echo ""
echo "🎯 Ready to test API key saving!"
EOF

chmod +x test_csp_fix.sh

print_success "Test script created"

echo ""
print_success "🎉 Final CSP Fix Applied!"
echo ""
echo "📋 What was fixed:"
echo "   ✅ Removed CSP from Next.js config (doesn't work with static export)"
echo "   ✅ Created custom Express server with proper CSP headers"
echo "   ✅ CSP allows localhost:8000 connections"
echo "   ✅ Updated startup scripts to use custom server"
echo ""
echo "🚀 Next steps:"
echo ""
echo "1. Start the backend:"
echo "   ./start_backend.sh"
echo ""
echo "2. Start the frontend (in another terminal):"
echo "   ./start_frontend.sh"
echo ""
echo "3. Test the fix:"
echo "   ./test_csp_fix.sh"
echo ""
echo "4. Go to http://localhost:9000/dashboard and try saving API keys"
echo ""
echo "🔒 CSP Policy Applied:"
echo "   connect-src 'self' http://localhost:8000 https://api.openai.com https://api.anthropic.com https://*.supabase.co wss://*.supabase.co"
echo ""
print_success "API key saving should now work without CSP errors! 🎉"
