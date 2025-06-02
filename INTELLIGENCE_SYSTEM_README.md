# 🧠 PlaybookWiz Intelligence System

## 🎯 Overview

The PlaybookWiz Intelligence System transforms static brand documents into an intelligent, queryable knowledge base with **semantic search**, **source attribution**, and **confidence scoring**.

## ✨ Key Features

### 🔍 **Semantic Search**
- Vector-based similarity search using ChromaDB
- Understands meaning and context, not just keywords
- Powered by `all-MiniLM-L6-v2` embedding model

### 📚 **Source Attribution**
- Every answer includes exact source passages
- Page numbers and document references
- Relevance scores for each source (0-100%)

### 🎯 **Confidence Scoring**
- AI confidence levels for each response
- Color-coded indicators (green/yellow/red)
- Processing time metrics

### 🤖 **Multi-Provider AI**
- OpenAI GPT-3.5 Turbo support
- Claude 3 Sonnet integration
- Users can configure their own API keys

### 📄 **Document Processing**
- PDF and PowerPoint support
- Intelligent text chunking (500 tokens, 50 overlap)
- Real-time vector indexing

## 🏗️ Architecture

```
Frontend (Next.js) → intelligent_main.py → intelligence_engine.py
                                        ↓
                    ChromaDB (vectors) + Supabase (metadata)
                                        ↓
                    OpenAI/Claude APIs
```

## 🚀 Quick Start

### 1. Run Setup Script
```bash
./setup_intelligence_system.sh
```

### 2. Configure Environment
Edit `.env` file:
```env
SUPABASE_URL=your-supabase-url
SUPABASE_SERVICE_KEY=your-service-key
ENCRYPTION_KEY=your-32-char-encryption-key
```

### 3. Setup Database Tables
Run these SQL scripts in Supabase:
- `backend/create_user_api_keys_table.sql`
- `backend/create_documents_table.sql`
- `backend/create_chat_sessions_table.sql`

### 4. Start Services
```bash
# Terminal 1: Backend
./start_backend.sh

# Terminal 2: Frontend
./start_frontend.sh
```

### 5. Access Application
- **Frontend**: http://localhost:9000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🔧 API Endpoints

### Document Management
- `POST /api/v1/documents/upload` - Upload & process documents
- `GET /api/v1/documents` - List user documents
- `DELETE /api/v1/documents/{id}` - Delete document

### Intelligent Chat
- `POST /api/v1/chat/intelligent` - AI chat with source attribution
- `POST /api/v1/search/passages` - Semantic passage search

### User Management
- `POST /api/v1/auth/api-keys` - Save encrypted API keys
- `GET /api/v1/stats` - User statistics

## 💡 Example Usage

### Query
```
"What is our primary brand color?"
```

### Response
```json
{
  "response": "Your primary brand color is Blue (#1E40AF)",
  "confidence": 0.95,
  "processing_time": 1.2,
  "provider_used": "openai",
  "sources": [
    {
      "passage": "The primary brand color is Blue (#1E40AF)...",
      "document_name": "Brand_Guidelines.pdf",
      "page_number": 12,
      "relevance_score": 0.98
    }
  ]
}
```

## 🔒 Security Features

- **Encrypted API Keys**: User API keys encrypted with Fernet
- **Row Level Security**: Supabase RLS policies
- **JWT Authentication**: Secure user sessions
- **CORS Protection**: Configured origins only

## 📊 Intelligence Engine Components

### `DocumentProcessor`
- PDF text extraction with PyPDF2
- PowerPoint processing with python-pptx
- Page/slide number preservation

### `TextChunker`
- Intelligent chunking with tiktoken
- Configurable chunk size and overlap
- Token-aware splitting

### `VectorDatabase`
- ChromaDB persistent storage
- Sentence transformer embeddings
- Metadata-rich search

### `AIResponseGenerator`
- Multi-provider support (OpenAI/Claude)
- Context-aware prompting
- Confidence calculation

## 🎨 Frontend Features

### Smart Chat Interface
- Real-time messaging
- Confidence bars with color coding
- Source attribution display
- Processing time indicators

### Document Management
- Upload progress tracking
- Processing status indicators
- Document statistics

### User Dashboard
- API key management
- Usage statistics
- System health monitoring

## 🔧 Configuration

### Environment Variables
```env
# Required
SUPABASE_URL=your-supabase-project-url
SUPABASE_SERVICE_KEY=your-service-role-key
ENCRYPTION_KEY=32-character-encryption-key

# Optional (users can add their own)
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-claude-key
```

### Customization Options
- Chunk size and overlap in `TextChunker`
- Embedding model in `VectorDatabase`
- AI model selection in `AIResponseGenerator`
- Confidence thresholds in frontend

## 🚀 Production Deployment

The system is production-ready with:
- Docker containerization
- Health check endpoints
- Structured logging
- Error handling
- Rate limiting ready
- Monitoring hooks

## 🎯 Next Steps

1. **Enhanced Analytics**: Usage tracking and insights
2. **Multi-Language**: Support for non-English documents
3. **Advanced Chunking**: Semantic-aware text splitting
4. **Batch Processing**: Multiple document uploads
5. **Export Features**: Save conversations and insights

---

**🎉 Your Brand Playbook Intelligence System is ready to transform static documents into intelligent, queryable knowledge!**
