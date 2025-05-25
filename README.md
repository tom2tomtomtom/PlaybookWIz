# Brand Playbook Intelligence App (PlaybookWiz)

A sophisticated web application that intelligently processes brand playbooks (PowerPoint and PDF formats), answers questions about brand guidelines, retrieves relevant passages verbatim, generates brand-aligned creative ideas, analyzes competitors, and identifies brand opportunities.

## 🎯 Core Features

- **Document Processing**: Ingest PowerPoint and PDF brand playbooks
- **Intelligent Q&A**: Answer natural language questions about brand guidelines
- **Brand-Aligned Ideation**: Generate creative ideas aligned with brand principles
- **Competitor Analysis**: Analyze competitor brands and provide insights
- **Opportunity Identification**: Identify strategic brand opportunities
- **Responsive Web Interface**: Modern, intuitive user experience

## 🏗️ Architecture

### Frontend
- **Framework**: Next.js 14 with TypeScript
- **UI Library**: Tailwind CSS + Headless UI
- **State Management**: Zustand
- **Data Visualization**: Chart.js + D3.js
- **Authentication**: NextAuth.js

### Backend
- **API**: FastAPI with Python 3.11+
- **Authentication**: JWT with role-based access control
- **Document Processing**: python-pptx, PyMuPDF, OpenCV
- **AI/ML**: OpenAI API, sentence-transformers, spaCy

### Databases
- **Relational**: PostgreSQL (user data, metadata)
- **Document**: MongoDB (processed documents)
- **Vector**: Pinecone (embeddings for semantic search)
- **Cache**: Redis (performance optimization)

### AI/ML Stack
- **LLM**: OpenAI GPT-4 for question answering and ideation
- **Embeddings**: sentence-transformers for semantic search
- **Computer Vision**: OpenCV + TensorFlow for visual analysis
- **NLP**: spaCy + Hugging Face transformers

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+

### Quick Setup

Run the automated setup script:
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### Manual Installation

1. **Clone and setup**
```bash
git clone <repository-url>
cd PlaybookWiz
```

2. **Environment Setup**
```bash
# Copy environment files
cp .env.example .env.local
cp backend/.env.example backend/.env

# Update with your API keys
# ANTHROPIC_API_KEY=your-anthropic-api-key-here
# OPENAI_API_KEY=your-openai-api-key-here (optional, for embeddings)
```

3. **Install Dependencies**
```bash
# Frontend
cd frontend && npm install

# Backend
cd ../backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

4. **Database Setup**
```bash
# Start databases with Docker
docker-compose up -d postgres mongodb redis

# Run migrations (from backend directory)
cd backend && source venv/bin/activate
alembic upgrade head
```

5. **Start Development Servers**
```bash
# Option 1: Start both (from root directory)
npm run dev

# Option 2: Start separately
# Terminal 1: Frontend
cd frontend && npm run dev

# Terminal 2: Backend
cd backend && source venv/bin/activate
uvicorn main:app --reload
```

## 📁 Project Structure

```
PlaybookWiz/
├── frontend/                 # Next.js application
│   ├── src/
│   │   ├── app/             # App router pages
│   │   ├── components/      # Reusable components
│   │   ├── lib/            # Utilities and configurations
│   │   └── types/          # TypeScript type definitions
│   ├── public/             # Static assets
│   └── package.json
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Core configurations
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   └── utils/          # Utility functions
│   ├── alembic/            # Database migrations
│   └── requirements.txt
├── shared/                  # Shared types and utilities
├── docker/                  # Docker configurations
├── docs/                    # Documentation
├── tests/                   # Test suites
└── scripts/                 # Setup and deployment scripts
```

## 🔧 Development

### Frontend Development
```bash
cd frontend
npm run dev          # Start development server
npm run build        # Build for production
npm run test         # Run tests
npm run lint         # Lint code
```

### Backend Development
```bash
cd backend
uvicorn main:app --reload    # Start development server
pytest                       # Run tests
black .                      # Format code
flake8                       # Lint code
```

## 🧪 Testing

Run `.tools/codex/setup.sh` before executing tests to ensure all dependencies are installed.

### Frontend Tests
- **Unit Tests**: Jest + React Testing Library
- **E2E Tests**: Playwright
- **Component Tests**: Storybook

### Backend Tests
- **Unit Tests**: pytest
- **Integration Tests**: pytest with test database
- **API Tests**: pytest + httpx

## 🚢 Deployment

### Docker Deployment
```bash
# Build and start all services
docker-compose up --build

# Production deployment
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Variables
See `.env.example` and `backend/.env.example` for required environment variables.

## 📚 API Documentation

- **Development**: http://localhost:8000/docs
- **Production**: https://your-domain.com/docs

## 🔐 Security

- JWT-based authentication
- Role-based access control (Admin, Brand Manager, Marketing Team)
- Data encryption at rest and in transit
- GDPR and CCPA compliance
- Comprehensive audit logging
- Rate limiting with SlowAPI
- Structured logging via structlog
- Error monitoring with Sentry

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support, email support@playbookwiz.com or create an issue in the repository.
