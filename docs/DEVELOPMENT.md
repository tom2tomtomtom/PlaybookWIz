# Development Guide

This guide provides detailed instructions for developing the PlaybookWiz Brand Playbook Intelligence App.

## 🏗️ Architecture Overview

PlaybookWiz uses a modern full-stack architecture with AI-powered intelligence:

### Frontend (Next.js + TypeScript)
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript for type safety
- **Styling**: Tailwind CSS with custom design system
- **State Management**: Zustand for global state
- **Data Fetching**: React Query for server state
- **UI Components**: Custom components with Headless UI

### Backend (FastAPI + Python)
- **Framework**: FastAPI for high-performance async API
- **Language**: Python 3.11+ with type hints
- **AI Integration**: Anthropic Claude API for intelligent processing
- **Document Processing**: PyMuPDF, python-pptx for content extraction
- **Authentication**: JWT with role-based access control

### AI/ML Stack
- **Primary LLM**: Anthropic Claude 3.5 Sonnet for reasoning and creativity
- **Embeddings**: OpenAI text-embedding-ada-002 or local sentence-transformers
- **Vector Search**: MongoDB with custom similarity search
- **Document Processing**: Multi-format support (PDF, PowerPoint, Word)

### Databases
- **PostgreSQL**: User data, documents metadata, sessions
- **MongoDB**: Document content, embeddings, brand analysis
- **Redis**: Caching, session storage, rate limiting

## 🔧 Development Setup

### Prerequisites
- Node.js 18+
- Python 3.11+
- Docker & Docker Compose
- Anthropic API key
- OpenAI API key (optional, for embeddings)

### Environment Configuration

1. **Get API Keys**
   ```bash
   # Anthropic API (required)
   # Sign up at: https://console.anthropic.com/
   ANTHROPIC_API_KEY=your-anthropic-api-key-here
   
   # OpenAI API (optional, for embeddings)
   # Sign up at: https://platform.openai.com/
   OPENAI_API_KEY=your-openai-api-key-here
   ```

2. **Configure Environment Files**
   ```bash
   # Frontend environment (.env.local)
   NEXT_PUBLIC_API_URL=http://localhost:8000
   NEXT_PUBLIC_APP_URL=http://localhost:3000
   
   # Backend environment (backend/.env)
   ANTHROPIC_API_KEY=your-anthropic-api-key-here
   OPENAI_API_KEY=your-openai-api-key-here
   DATABASE_URL=postgresql://playbookwiz:password@localhost:5432/playbookwiz
   MONGODB_URL=mongodb://localhost:27017/playbookwiz
   REDIS_URL=redis://localhost:6379
   ```

### Quick Start

1. **Run Setup Script**
   ```bash
   chmod +x scripts/setup.sh
   ./scripts/setup.sh
   ```

2. **Start Development**
   ```bash
   # Start all services
   npm run dev
   
   # Or start individually
   npm run dev:frontend  # Frontend only
   npm run dev:backend   # Backend only
   ```

3. **Access Applications**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## 🧠 AI Integration with Anthropic Claude

### Core AI Service

The `AIService` class handles all AI interactions:

```python
# backend/app/services/ai_service.py
from anthropic import AsyncAnthropic

class AIService:
    def __init__(self):
        self.anthropic_client = AsyncAnthropic(
            api_key=settings.ANTHROPIC_API_KEY
        )
    
    async def answer_question(self, question: str, context: str):
        response = await self.anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1500,
            messages=[{
                "role": "user",
                "content": f"Context: {context}\n\nQuestion: {question}"
            }]
        )
        return response.content[0].text
```

### Creative Personas

PlaybookWiz implements creative personas for enhanced ideation:

- **Aiden**: Strategic Brand Visionary
- **Maya**: Creative Innovation Catalyst  
- **Leo**: Data-Driven Strategist
- **Zara**: Disruptive Innovation Expert

### Document Processing Pipeline

1. **Upload & Validation**
   - File type validation (PDF, PPT, PPTX)
   - Size limits (100MB max)
   - Security scanning

2. **Content Extraction**
   - Text extraction with formatting
   - Image and chart detection
   - Table structure preservation
   - Metadata extraction

3. **AI Processing**
   - Text chunking for embeddings
   - Brand element analysis with Claude
   - Semantic embedding generation
   - Vector storage in MongoDB

4. **Indexing & Search**
   - Vector similarity search
   - Hybrid retrieval (semantic + keyword)
   - Relevance scoring

## 🎨 Frontend Development

### Component Structure

```
frontend/src/
├── app/                    # Next.js App Router pages
├── components/
│   ├── ui/                # Reusable UI components
│   ├── forms/             # Form components
│   ├── layout/            # Layout components
│   └── features/          # Feature-specific components
├── lib/                   # Utilities and configurations
├── hooks/                 # Custom React hooks
├── stores/                # Zustand stores
└── types/                 # TypeScript type definitions
```

### Key Components

1. **FileUpload**: Drag-and-drop document upload
2. **QuestionInterface**: AI-powered Q&A interface
3. **IdeationWorkspace**: Creative ideation environment
4. **DocumentViewer**: Processed document display
5. **AnalyticsDashboard**: Usage and insights

### State Management

```typescript
// stores/documentStore.ts
import { create } from 'zustand';

interface DocumentStore {
  documents: Document[];
  currentDocument: Document | null;
  uploadDocument: (file: File) => Promise<void>;
  selectDocument: (id: string) => void;
}

export const useDocumentStore = create<DocumentStore>((set, get) => ({
  documents: [],
  currentDocument: null,
  uploadDocument: async (file) => {
    // Upload logic
  },
  selectDocument: (id) => {
    // Selection logic
  },
}));
```

## 🔧 Backend Development

### API Structure

```
backend/app/
├── api/
│   └── api_v1/
│       └── endpoints/     # API route handlers
├── core/                  # Core configurations
├── models/                # Database models
├── schemas/               # Pydantic schemas
├── services/              # Business logic
└── utils/                 # Utility functions
```

### Key Services

1. **DocumentService**: Document processing and management
2. **AIService**: AI integration and processing
3. **QuestionService**: Q&A functionality
4. **IdeationService**: Creative ideation features
5. **AnalysisService**: Competitor and opportunity analysis

### Database Models

```python
# models/document.py
from sqlalchemy import Column, String, Integer, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    status = Column(String, nullable=False)
    metadata = Column(JSON)
    created_at = Column(DateTime, nullable=False)
```

## 🧪 Testing

### Frontend Testing

```bash
cd frontend
npm test              # Run Jest tests
npm run test:watch    # Watch mode
npm run test:coverage # Coverage report
```

### Backend Testing

```bash
cd backend
source venv/bin/activate
pytest                # Run all tests
pytest -v             # Verbose output
pytest --cov         # Coverage report
```

### Test Structure

```
tests/
├── frontend/
│   ├── components/    # Component tests
│   ├── pages/         # Page tests
│   └── utils/         # Utility tests
└── backend/
    ├── api/           # API endpoint tests
    ├── services/      # Service tests
    └── models/        # Model tests
```

## 🚀 Deployment

### Docker Deployment

```bash
# Development
docker-compose up --build

# Production
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Variables

Ensure all required environment variables are set:

- `ANTHROPIC_API_KEY`: Your Anthropic API key
- `OPENAI_API_KEY`: Your OpenAI API key (optional)
- `DATABASE_URL`: PostgreSQL connection string
- `MONGODB_URL`: MongoDB connection string
- `REDIS_URL`: Redis connection string

## 📊 Monitoring & Debugging

### Logging

```python
import logging
logger = logging.getLogger(__name__)

# Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
logger.info("Processing document", extra={"document_id": doc_id})
```

### Performance Monitoring

- API response times
- Document processing duration
- AI service latency
- Database query performance

### Error Tracking

- Sentry integration for error tracking
- Structured logging with context
- User feedback collection

## 🔐 Security Considerations

1. **API Security**
   - JWT authentication
   - Rate limiting
   - Input validation
   - CORS configuration

2. **Data Protection**
   - Encryption at rest
   - Secure file storage
   - PII handling
   - GDPR compliance

3. **AI Safety**
   - Input sanitization
   - Output filtering
   - Content moderation
   - Usage monitoring

## 📚 Additional Resources

- [Anthropic API Documentation](https://docs.anthropic.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
