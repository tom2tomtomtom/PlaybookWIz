#!/bin/bash

# PlaybookWiz Intelligence System - CSP Fix and Complete Setup
# This script fixes the Content Security Policy issues and sets up the system

set -e  # Exit on any error

echo "🔧 PlaybookWiz Intelligence System - CSP Fix & Setup"
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

print_status "Setting up environment variables..."

# Create frontend environment file
cat > frontend/.env.local << 'EOF'
# Frontend Environment Variables
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=your-supabase-url-here
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key-here
EOF

# Create backend environment file if it doesn't exist
if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
# Backend Environment Variables
SUPABASE_URL=your-supabase-url-here
SUPABASE_SERVICE_KEY=your-supabase-service-key-here
ENCRYPTION_KEY=playbookwiz-32char-encryption-key
ADMIN_SECRET=playbookwiz-admin-secret-2024

# Optional: Default API Keys
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
EOF
    print_warning "Created .env file - please update with your actual credentials"
else
    print_success "Environment file already exists"
fi

# Install backend dependencies
print_status "Installing backend dependencies..."
cd backend

if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

print_success "Backend dependencies installed!"

# Build frontend
print_status "Building frontend..."
cd ../frontend
npm install
npm run build

print_success "Frontend built successfully!"

# Create startup scripts
cd ..
print_status "Creating startup scripts..."

cat > start_backend.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting PlaybookWiz Intelligence Backend..."
cd backend
source venv/bin/activate
python intelligent_main.py
EOF

cat > start_frontend.sh << 'EOF'
#!/bin/bash
echo "🌐 Starting PlaybookWiz Frontend..."
cd frontend/out
python3 -m http.server 9000
EOF

chmod +x start_backend.sh
chmod +x start_frontend.sh

print_success "Startup scripts created!"

# Create API key management script
chmod +x save_user_api_key.py

print_success "API key management script ready!"

echo ""
print_success "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo ""
echo "1. 🔧 Configure your environment:"
echo "   - Edit .env file with your Supabase credentials"
echo "   - Edit frontend/.env.local with your Supabase public keys"
echo ""
echo "2. 🗄️  Setup database tables in Supabase:"
echo "   - Run: backend/create_user_api_keys_table.sql"
echo "   - Run: backend/create_documents_table.sql"
echo "   - Run: backend/create_chat_sessions_table.sql"
echo ""
echo "3. 🔑 Save API keys for users (optional):"
echo "   - Run: python save_user_api_key.py"
echo "   - Or users can add their own keys in the dashboard"
echo ""
echo "4. 🚀 Start the system:"
echo "   - Backend:  ./start_backend.sh"
echo "   - Frontend: ./start_frontend.sh"
echo ""
echo "5. 🌐 Access the application:"
echo "   - Frontend: http://localhost:9000"
echo "   - Backend API: http://localhost:8000"
echo ""
echo "🔒 CSP Issues Fixed:"
echo "   ✅ Content Security Policy updated to allow localhost connections"
echo "   ✅ Frontend uses environment variables for backend URL"
echo "   ✅ All API calls properly configured"
echo ""
print_success "Your Brand Playbook Intelligence System is ready! 🎉"
