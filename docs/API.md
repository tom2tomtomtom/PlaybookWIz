# PlaybookWiz API Documentation

This document provides comprehensive documentation for the PlaybookWiz Brand Playbook Intelligence API.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://api.playbookwiz.com`

## Authentication

All API endpoints (except health checks) require authentication using JWT tokens.

### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Using the Token
Include the token in the Authorization header:
```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

## Document Management

### Upload Document
Upload and process a brand playbook document.

```http
POST /api/v1/documents/upload
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: [binary file data]
```

**Supported formats**: PDF, PPT, PPTX, DOC, DOCX
**Max file size**: 100MB

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "filename": "brand-guidelines.pdf",
  "file_size": 2048576,
  "file_type": "pdf",
  "status": "processing",
  "created_at": "2024-01-15T10:30:00Z",
  "page_count": null,
  "word_count": null
}
```

### List Documents
Get user's uploaded documents.

```http
GET /api/v1/documents?skip=0&limit=20&status=completed
Authorization: Bearer {token}
```

**Query Parameters:**
- `skip` (int): Number of documents to skip (pagination)
- `limit` (int): Maximum number of documents to return
- `status` (string): Filter by processing status (`pending`, `processing`, `completed`, `failed`)

**Response:**
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "filename": "brand-guidelines.pdf",
    "file_size": 2048576,
    "file_type": "pdf",
    "status": "completed",
    "created_at": "2024-01-15T10:30:00Z",
    "page_count": 25,
    "word_count": 5420
  }
]
```

### Get Document Details
Retrieve details for a specific document.

```http
GET /api/v1/documents/{document_id}
Authorization: Bearer {token}
```

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "filename": "brand-guidelines.pdf",
  "file_size": 2048576,
  "file_type": "pdf",
  "status": "completed",
  "created_at": "2024-01-15T10:30:00Z",
  "page_count": 25,
  "word_count": 5420,
  "metadata": {
    "title": "Brand Guidelines 2024",
    "author": "Marketing Team",
    "creation_date": "2024-01-10T00:00:00Z"
  }
}
```

### Get Document Content
Retrieve processed content from a document.

```http
GET /api/v1/documents/{document_id}/content?page=1&section=colors
Authorization: Bearer {token}
```

**Query Parameters:**
- `page` (int): Specific page number
- `section` (string): Specific section name

**Response:**
```json
{
  "document_id": "123e4567-e89b-12d3-a456-426614174000",
  "content": {
    "text": "Brand colors are essential...",
    "pages": [
      {
        "page_number": 1,
        "text": "Page content...",
        "images": [],
        "tables": []
      }
    ],
    "brand_elements": {
      "colors": ["#2563EB", "#10B981"],
      "fonts": ["Inter", "Roboto"],
      "guidelines": ["Use primary color for headers"]
    }
  }
}
```

## Question Answering

### Ask Question
Ask a question about brand playbooks using AI.

```http
POST /api/v1/questions/ask
Authorization: Bearer {token}
Content-Type: application/json

{
  "question": "What are the primary brand colors?",
  "document_ids": ["123e4567-e89b-12d3-a456-426614174000"],
  "conversation_id": null,
  "preferences": {
    "include_sources": true,
    "max_sources": 3
  }
}
```

**Response:**
```json
{
  "id": "456e7890-e89b-12d3-a456-426614174001",
  "question": "What are the primary brand colors?",
  "answer": "Based on the brand guidelines, the primary brand colors are:\n\n1. **Primary Blue**: #2563EB - Used for headers and primary actions\n2. **Secondary Green**: #10B981 - Used for success states and highlights\n3. **Accent Orange**: #F59E0B - Used for call-to-action elements\n\nThese colors should be used consistently across all brand materials to maintain visual identity.",
  "confidence": 0.95,
  "sources": [
    {
      "document_id": "123e4567-e89b-12d3-a456-426614174000",
      "text": "Primary colors: Blue (#2563EB), Green (#10B981), Orange (#F59E0B)",
      "relevance_score": 0.98,
      "page_numbers": [3, 4]
    }
  ],
  "conversation_id": "789e0123-e89b-12d3-a456-426614174002",
  "created_at": "2024-01-15T11:00:00Z"
}
```

### Get Question History
Retrieve user's question history.

```http
GET /api/v1/questions/history?skip=0&limit=20&conversation_id={uuid}
Authorization: Bearer {token}
```

**Response:**
```json
[
  {
    "id": "456e7890-e89b-12d3-a456-426614174001",
    "question": "What are the primary brand colors?",
    "answer": "Based on the brand guidelines...",
    "confidence": 0.95,
    "conversation_id": "789e0123-e89b-12d3-a456-426614174002",
    "created_at": "2024-01-15T11:00:00Z"
  }
]
```

### Suggest Questions
Get AI-generated question suggestions based on document content.

```http
POST /api/v1/questions/suggest
Authorization: Bearer {token}
Content-Type: application/json

{
  "document_ids": ["123e4567-e89b-12d3-a456-426614174000"],
  "count": 5
}
```

**Response:**
```json
{
  "suggestions": [
    "What are the primary brand colors and their usage guidelines?",
    "How should the brand voice be applied in marketing materials?",
    "What are the logo usage requirements and restrictions?",
    "Who is the target audience for this brand?",
    "What are the key brand values and how should they be communicated?"
  ]
}
```

## Creative Ideation

### Generate Ideas
Generate brand-aligned creative ideas using AI personas.

```http
POST /api/v1/ideation/generate
Authorization: Bearer {token}
Content-Type: application/json

{
  "prompt": "Create a social media campaign for our new product launch",
  "document_ids": ["123e4567-e89b-12d3-a456-426614174000"],
  "objective": "increase_awareness",
  "target_audience": "tech_professionals",
  "use_personas": true,
  "selected_personas": ["aiden", "maya"],
  "creativity_level": "high",
  "count": 3
}
```

**Response:**
```json
{
  "session_id": "abc12345-e89b-12d3-a456-426614174003",
  "ideas": [
    {
      "id": 1,
      "title": "Tech Innovation Spotlight Series",
      "description": "A weekly social media series highlighting how our product solves real tech challenges...",
      "persona": "aiden",
      "rationale": "This approach aligns with our brand's innovation focus while addressing the target audience's pain points...",
      "implementation": {
        "platforms": ["LinkedIn", "Twitter"],
        "content_types": ["video", "infographic"],
        "timeline": "8 weeks"
      },
      "brand_alignment_score": 0.92
    }
  ],
  "request": {
    "prompt": "Create a social media campaign for our new product launch",
    "objective": "increase_awareness",
    "use_personas": true
  },
  "created_at": "2024-01-15T12:00:00Z"
}
```

### Persona Dialogue
Generate philosophical dialogue between personas to enhance creativity.

```http
POST /api/v1/ideation/personas/dialogue
Authorization: Bearer {token}
Content-Type: application/json

{
  "topic": "The future of brand authenticity in digital spaces",
  "personas": ["aiden", "zara"],
  "context": "Preparing for a campaign about authentic brand connections"
}
```

**Response:**
```json
{
  "dialogue": [
    {
      "persona": "aiden",
      "message": "I've been contemplating how authenticity in branding has evolved. In our hyperconnected world, consumers can sense manufactured authenticity from miles away..."
    },
    {
      "persona": "zara",
      "message": "Exactly! But here's where it gets interesting - what if we flip the script entirely? Instead of trying to appear authentic, what if brands embraced their constructed nature?"
    }
  ],
  "topic": "The future of brand authenticity in digital spaces",
  "personas": ["aiden", "zara"]
}
```

### Enhance Creativity
Apply creativity enhancement techniques to existing ideas.

```http
POST /api/v1/ideation/enhance
Authorization: Bearer {token}
Content-Type: application/json

{
  "session_id": "abc12345-e89b-12d3-a456-426614174003",
  "enhancement_type": "emotional_depth"
}
```

**Enhancement Types:**
- `emotional_depth`: Add emotional resonance
- `pattern_breaking`: Subvert expectations  
- `philosophical`: Add philosophical depth
- `cultural_relevance`: Enhance cultural connections

## Brand Analysis

### Analyze Competitors
Analyze competitor brands and provide insights.

```http
POST /api/v1/analysis/competitors
Authorization: Bearer {token}
Content-Type: application/json

{
  "competitors": ["Apple", "Google", "Microsoft"],
  "analysis_type": "positioning",
  "document_ids": ["123e4567-e89b-12d3-a456-426614174000"]
}
```

**Response:**
```json
{
  "analysis": {
    "competitive_landscape": "The technology sector shows clear differentiation strategies...",
    "positioning_gaps": [
      "Sustainability-focused innovation",
      "Privacy-first approach",
      "Accessibility leadership"
    ],
    "recommendations": [
      "Emphasize unique value proposition in sustainability",
      "Develop privacy-centric messaging",
      "Create accessibility-focused campaigns"
    ]
  },
  "competitors": [
    {
      "name": "Apple",
      "positioning": "Premium innovation and design",
      "strengths": ["Brand loyalty", "Design excellence"],
      "weaknesses": ["High pricing", "Limited accessibility"]
    }
  ]
}
```

### Identify Opportunities
Identify strategic brand opportunities.

```http
POST /api/v1/analysis/opportunities
Authorization: Bearer {token}
Content-Type: application/json

{
  "document_ids": ["123e4567-e89b-12d3-a456-426614174000"],
  "market_context": "B2B technology sector",
  "analysis_depth": "comprehensive"
}
```

**Response:**
```json
{
  "opportunities": [
    {
      "type": "market_gap",
      "title": "Sustainable Technology Leadership",
      "description": "Opportunity to lead in environmentally conscious technology solutions...",
      "potential_impact": "high",
      "implementation_complexity": "medium",
      "timeline": "6-12 months"
    }
  ],
  "strategic_recommendations": [
    "Develop sustainability-focused product line",
    "Create thought leadership content on green technology",
    "Partner with environmental organizations"
  ]
}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters",
  "error_code": "INVALID_REQUEST"
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication required",
  "error_code": "UNAUTHORIZED"
}
```

### 403 Forbidden
```json
{
  "detail": "Insufficient permissions",
  "error_code": "FORBIDDEN"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found",
  "error_code": "NOT_FOUND"
}
```

### 429 Too Many Requests
```json
{
  "detail": "Rate limit exceeded",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "retry_after": 60
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error",
  "error_code": "INTERNAL_ERROR",
  "error_id": "uuid-for-tracking"
}
```

## Rate Limits

- **General API**: 100 requests per hour per user
- **Document Upload**: 10 uploads per hour per user
- **AI Operations**: 50 requests per hour per user

## SDKs and Libraries

### Python SDK
```python
from playbookwiz import PlaybookWizClient

client = PlaybookWizClient(api_key="your-api-key")
result = await client.ask_question(
    question="What are the brand colors?",
    document_ids=["doc-id"]
)
```

### JavaScript SDK
```javascript
import { PlaybookWizClient } from '@playbookwiz/sdk';

const client = new PlaybookWizClient({ apiKey: 'your-api-key' });
const result = await client.askQuestion({
  question: 'What are the brand colors?',
  documentIds: ['doc-id']
});
```
