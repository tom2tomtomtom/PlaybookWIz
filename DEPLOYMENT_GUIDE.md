# 🚀 PlaybookWiz Intelligence System - Deployment Guide

## 📋 Prerequisites

### Required Services
- **Supabase Account**: For authentication and database
- **OpenAI API Key**: For GPT-3.5 integration (optional - users can add their own)
- **Claude API Key**: For Claude integration (optional - users can add their own)

### System Requirements
- **Python 3.11+**
- **Node.js 18+**
- **4GB+ RAM** (for embedding models)
- **2GB+ Storage** (for vector database)

## 🔧 Step-by-Step Setup

### 1. Clone and Setup
```bash
git clone <your-repo>
cd PlaybookWiz
chmod +x setup_intelligence_system.sh
./setup_intelligence_system.sh
```

### 2. Configure Supabase

#### A. Create Supabase Project
1. Go to [supabase.com](https://supabase.com)
2. Create new project
3. Note your project URL and service key

#### B. Setup Database Tables
Run these SQL scripts in Supabase SQL Editor:

**1. User API Keys Table:**
```sql
-- Copy content from: backend/create_user_api_keys_table.sql
```

**2. Documents Table:**
```sql
-- Copy content from: backend/create_documents_table.sql
```

**3. Chat Sessions Table:**
```sql
-- Copy content from: backend/create_chat_sessions_table.sql
```

### 3. Environment Configuration

Edit `.env` file:
```env
# Supabase Configuration (Required)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key

# Encryption Key (Required)
ENCRYPTION_KEY=your-32-character-encryption-key-here

# Optional: Default API Keys
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-claude-key
```

### 4. Test the System

```bash
# Test intelligence engine
cd backend
python test_intelligence_engine.py

# Expected output: All tests should pass ✅
```

### 5. Start Services

#### Backend (Terminal 1):
```bash
./start_backend.sh
# Or manually:
cd backend
source venv/bin/activate
python intelligent_main.py
```

#### Frontend (Terminal 2):
```bash
./start_frontend.sh
# Or manually:
cd frontend/out
python3 -m http.server 9000
```

## 🌐 Access Points

- **Frontend**: http://localhost:9000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🔍 Verification Steps

### 1. Backend Health Check
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy", "service": "PlaybookWiz Intelligence API"}
```

### 2. Frontend Access
- Navigate to http://localhost:9000
- Should see PlaybookWiz login page
- Sign up/sign in with Supabase auth

### 3. Upload Test Document
1. Login to the application
2. Go to Dashboard → Upload Documents
3. Upload a PDF or PowerPoint file
4. Verify processing completes

### 4. Test Intelligent Chat
1. Add your OpenAI or Claude API key in dashboard
2. Go to AI Chat
3. Ask: "What is this document about?"
4. Verify response with sources and confidence

## 🔒 Security Configuration

### API Key Encryption
- User API keys are encrypted with Fernet
- Encryption key should be 32 characters
- Store securely in production

### Supabase Security
- Row Level Security (RLS) enabled
- Users can only access their own data
- JWT authentication required

### CORS Configuration
```python
# In intelligent_main.py
allowed_origins = [
    "http://localhost:9000",
    "http://localhost:3000", 
    "https://your-production-domain.com"
]
```

## 📊 Monitoring & Logs

### Backend Logs
```bash
# View real-time logs
tail -f backend/logs/app.log

# Key log patterns:
# - Document processing: "Processing document: filename"
# - Vector operations: "Added X chunks to vector database"
# - AI responses: "Processing intelligent chat for user"
```

### Health Monitoring
- `/health` endpoint for basic health
- `/api/v1/stats` for user statistics
- ChromaDB status in vector database

## 🚀 Production Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Variables for Production
```env
# Production Supabase
SUPABASE_URL=https://your-prod-project.supabase.co
SUPABASE_SERVICE_KEY=your-prod-service-key

# Secure encryption key
ENCRYPTION_KEY=generate-secure-32-char-key

# Optional: System-wide API keys
OPENAI_API_KEY=your-production-openai-key
ANTHROPIC_API_KEY=your-production-claude-key

# Production settings
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### Scaling Considerations
- **Vector Database**: ChromaDB scales to millions of documents
- **API Rate Limits**: Implement rate limiting for production
- **Caching**: Add Redis for response caching
- **Load Balancing**: Use multiple backend instances

## 🔧 Troubleshooting

### Common Issues

#### 1. "No module named 'sentence_transformers'"
```bash
cd backend
source venv/bin/activate
pip install sentence-transformers
```

#### 2. "ChromaDB connection failed"
```bash
# Check ChromaDB directory
ls -la backend/chroma_db/
# Should exist and be writable
```

#### 3. "Supabase authentication failed"
- Verify SUPABASE_URL and SUPABASE_SERVICE_KEY
- Check Supabase project is active
- Ensure RLS policies are created

#### 4. "API key decryption error"
- Verify ENCRYPTION_KEY is 32 characters
- Check user has saved API keys in dashboard

### Debug Mode
```bash
# Run backend in debug mode
cd backend
source venv/bin/activate
uvicorn intelligent_main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
```

## 📈 Performance Optimization

### Vector Database
- **Embedding Model**: `all-MiniLM-L6-v2` (384 dimensions)
- **Chunk Size**: 500 tokens with 50 token overlap
- **Search Results**: Top 5 most relevant passages

### AI Response Generation
- **OpenAI**: GPT-3.5-turbo (fast, cost-effective)
- **Claude**: Claude-3-sonnet (high quality)
- **Max Tokens**: 500 per response
- **Temperature**: 0.3 (focused responses)

### Caching Strategy
- Vector embeddings cached in ChromaDB
- API responses can be cached with Redis
- Document processing results stored in Supabase

## 🎯 Success Metrics

Your system is working correctly when:

✅ **Document Upload**: PDFs/PowerPoints process within 30 seconds  
✅ **Vector Search**: Sub-second response times  
✅ **AI Responses**: Generated within 3 seconds  
✅ **Source Attribution**: Every answer includes relevant sources  
✅ **Confidence Scores**: Accurate confidence levels (0-100%)  
✅ **User Experience**: Smooth chat interface with real-time updates  

---

**🎉 Your Brand Playbook Intelligence System is now live and ready to transform static documents into intelligent, queryable knowledge!**
