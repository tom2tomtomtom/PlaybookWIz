#!/bin/bash

# PlaybookWiz Intelligence System Setup Script
# This script sets up the complete Brand Playbook Intelligence System

set -e  # Exit on any error

echo "🚀 Setting up PlaybookWiz Intelligence System..."

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

# Check if we're in the right directory
if [ ! -f "backend/intelligent_main.py" ]; then
    print_error "Please run this script from the PlaybookWiz root directory"
    exit 1
fi

# Step 1: Install Backend Dependencies
print_status "Installing backend dependencies..."
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Install requirements
print_status "Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

print_success "Backend dependencies installed!"

# Step 2: Setup Frontend
print_status "Setting up frontend..."
cd ../frontend

# Install Node.js dependencies
print_status "Installing Node.js dependencies..."
npm install

# Build the frontend
print_status "Building frontend..."
npm run build

print_success "Frontend built successfully!"

# Step 3: Environment Setup
cd ..
print_status "Setting up environment variables..."

if [ ! -f ".env" ]; then
    print_warning "No .env file found. Creating template..."
    cat > .env << EOF
# Supabase Configuration
SUPABASE_URL=your-supabase-url-here
SUPABASE_SERVICE_KEY=your-supabase-service-key-here

# Encryption Key for API Keys
ENCRYPTION_KEY=playbookwiz-32char-encryption-key

# Optional: Default API Keys (users can override these)
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
EOF
    print_warning "Please edit .env file with your actual credentials"
else
    print_success "Environment file already exists"
fi

# Step 4: Database Setup Instructions
print_status "Database setup instructions:"
echo ""
echo "📋 Please run these SQL scripts in your Supabase SQL editor:"
echo ""
echo "1. Create user_api_keys table:"
echo "   Run: backend/create_user_api_keys_table.sql"
echo ""
echo "2. Create documents table:"
echo "   Run: backend/create_documents_table.sql"
echo ""
echo "3. Create chat_sessions table:"
echo "   Run: backend/create_chat_sessions_table.sql"
echo ""

# Step 5: Create startup scripts
print_status "Creating startup scripts..."

# Backend startup script
cat > start_backend.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting PlaybookWiz Intelligence Backend..."
cd backend
source venv/bin/activate
python intelligent_main.py
EOF

# Frontend startup script
cat > start_frontend.sh << 'EOF'
#!/bin/bash
echo "🌐 Starting PlaybookWiz Frontend..."
cd frontend/out
python3 -m http.server 9000
EOF

# Make scripts executable
chmod +x start_backend.sh
chmod +x start_frontend.sh

print_success "Startup scripts created!"

# Step 6: Create ChromaDB directory
print_status "Creating ChromaDB directory..."
mkdir -p backend/chroma_db
print_success "ChromaDB directory created!"

# Final instructions
echo ""
print_success "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo ""
echo "1. 🔧 Configure your environment:"
echo "   - Edit .env file with your Supabase credentials"
echo "   - Add your OpenAI/Claude API keys (optional - users can add their own)"
echo ""
echo "2. 🗄️  Setup database tables:"
echo "   - Run the SQL scripts in your Supabase dashboard"
echo ""
echo "3. 🚀 Start the system:"
echo "   - Backend:  ./start_backend.sh"
echo "   - Frontend: ./start_frontend.sh"
echo ""
echo "4. 🌐 Access the application:"
echo "   - Frontend: http://localhost:9000"
echo "   - Backend API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo ""
echo "🎯 Features ready:"
echo "   ✅ Vector-based semantic search"
echo "   ✅ Source attribution with page numbers"
echo "   ✅ Confidence scoring"
echo "   ✅ Multi-document support"
echo "   ✅ OpenAI & Claude integration"
echo "   ✅ Real-time chat interface"
echo ""
print_success "Your Brand Playbook Intelligence System is ready! 🎉"
EOF
