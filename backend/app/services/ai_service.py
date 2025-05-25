"""
AI Service using Anthropic Claude API.

This service handles all AI-related functionality including:
- Document content processing and embedding generation
- Question answering with retrieval-augmented generation (RAG)
- Brand-aligned creative ideation
- Competitor analysis
- Opportunity identification
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from uuid import UUID
import json
import asyncio

import anthropic
from anthropic import AsyncAnthropic
import openai
from sentence_transformers import SentenceTransformer
import numpy as np

from app.core.config import settings
from app.core.database import get_mongodb, get_redis

logger = logging.getLogger(__name__)


class AIService:
    """AI service using Anthropic Claude for intelligent processing."""
    
    def __init__(self):
        self.anthropic_client = None
        self.openai_client = None  # For embeddings only
        self.embedding_model = None
        self.mongodb = None
        self.redis = None
        
        # Creative personas for ideation
        self.personas = {
            "aiden": {
                "name": "Aiden",
                "role": "Strategic Brand Visionary",
                "personality": "Analytical, forward-thinking, and philosophically inclined",
                "expertise": "Brand strategy, market positioning, cultural trends",
                "approach": "Combines deep analysis with creative intuition"
            },
            "maya": {
                "name": "Maya",
                "role": "Creative Innovation Catalyst",
                "personality": "Imaginative, empathetic, and culturally aware",
                "expertise": "Creative campaigns, storytelling, audience connection",
                "approach": "Human-centered design with emotional resonance"
            },
            "leo": {
                "name": "Leo",
                "role": "Data-Driven Strategist",
                "personality": "Logical, methodical, and insight-focused",
                "expertise": "Market research, competitive analysis, performance metrics",
                "approach": "Evidence-based recommendations with clear rationale"
            },
            "zara": {
                "name": "Zara",
                "role": "Disruptive Innovation Expert",
                "personality": "Bold, unconventional, and trend-setting",
                "expertise": "Emerging technologies, cultural shifts, breakthrough ideas",
                "approach": "Challenges assumptions and explores new possibilities"
            }
        }
    
    async def initialize(self):
        """Initialize AI service components."""
        try:
            # Initialize Anthropic client
            self.anthropic_client = AsyncAnthropic(
                api_key=settings.ANTHROPIC_API_KEY
            )
            
            # Initialize OpenAI client for embeddings (if available)
            if settings.OPENAI_API_KEY:
                self.openai_client = openai.AsyncOpenAI(
                    api_key=settings.OPENAI_API_KEY
                )
            
            # Initialize embedding model
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Get database connections
            self.mongodb = await get_mongodb()
            self.redis = await get_redis()
            
            logger.info("AI service initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing AI service: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup AI service resources."""
        # Close any open connections if needed
        logger.info("AI service cleanup completed")

    async def get_document_content(
        self,
        document_id: UUID,
        page: Optional[int] = None,
        section: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Retrieve processed document content."""
        try:
            cache_key = f"document_content:{document_id}"
            cached = await self.redis.get(cache_key)
            if cached:
                content = json.loads(cached)
            else:
                collection = self.mongodb["document_content"]
                record = await collection.find_one({"document_id": str(document_id)})
                if not record:
                    return None
                content = record.get("content", {})
                await self.redis.setex(
                    cache_key,
                    settings.CACHE_TTL,
                    json.dumps(content, default=str),
                )

            if page is not None:
                for p in content.get("pages", []):
                    if p.get("page_number") == page:
                        return p
                return None

            if section:
                return content.get(section)

            return content
        except Exception as e:
            logger.error(f"Error retrieving document content: {e}")
            return None

    async def delete_document_embeddings(self, document_id: UUID):
        """Delete stored embeddings and cached content for a document."""
        try:
            await self.redis.delete(f"document_content:{document_id}")
            await self.mongodb["document_embeddings"].delete_many({"document_id": str(document_id)})
            await self.mongodb["brand_analysis"].delete_many({"document_id": str(document_id)})
            await self.mongodb["document_content"].delete_many({"document_id": str(document_id)})
        except Exception as e:
            logger.error(f"Error deleting document data: {e}")
    
    async def process_document_content(
        self,
        document_id: UUID,
        content: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Process document content and generate embeddings.
        
        Args:
            document_id: Document identifier
            content: Extracted document content
            
        Returns:
            Processing results and metadata
        """
        try:
            # Extract text content
            text_content = content.get("text", "")
            
            # Split text into chunks for embedding
            chunks = self._split_text_into_chunks(text_content)
            
            # Generate embeddings for each chunk
            embeddings = []
            for i, chunk in enumerate(chunks):
                embedding = await self._generate_embedding(chunk)
                
                chunk_data = {
                    "document_id": str(document_id),
                    "chunk_id": f"{document_id}_{i}",
                    "text": chunk,
                    "embedding": embedding.tolist(),
                    "metadata": {
                        "chunk_index": i,
                        "chunk_length": len(chunk),
                        "page_numbers": self._extract_page_numbers(chunk, content),
                    }
                }
                embeddings.append(chunk_data)
            
            # Store embeddings in MongoDB
            if embeddings:
                collection = self.mongodb["document_embeddings"]
                await collection.insert_many(embeddings)
            
            # Extract and store brand elements
            brand_analysis = await self._analyze_brand_elements(content)
            
            # Store brand analysis
            brand_collection = self.mongodb["brand_analysis"]
            await brand_collection.insert_one({
                "document_id": str(document_id),
                "analysis": brand_analysis,
            })

            # Persist full processed content in MongoDB for later analysis
            content_collection = self.mongodb["document_content"]
            await content_collection.update_one(
                {"document_id": str(document_id)},
                {"$set": {"content": content}},
                upsert=True,
            )
            
            # Cache processed content
            await self.redis.setex(
                f"document_content:{document_id}",
                settings.CACHE_TTL,
                json.dumps(content, default=str)
            )
            
            return {
                "chunks_processed": len(chunks),
                "embeddings_generated": len(embeddings),
                "brand_elements_found": len(brand_analysis.get("elements", [])),
            }
            
        except Exception as e:
            logger.error(f"Error processing document content: {e}")
            raise
    
    def _split_text_into_chunks(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks for embedding."""
        if not text:
            return []
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings near the chunk boundary
                for i in range(end, max(start + chunk_size - 200, start), -1):
                    if text[i] in '.!?':
                        end = i + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
            
            if start >= len(text):
                break
        
        return chunks
    
    async def _generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for text."""
        try:
            if self.openai_client:
                # Use OpenAI embeddings if available
                response = await self.openai_client.embeddings.create(
                    model=settings.OPENAI_EMBEDDING_MODEL,
                    input=text
                )
                return np.array(response.data[0].embedding)
            else:
                # Use local sentence transformer
                return self.embedding_model.encode(text)
                
        except Exception as e:
            logger.warning(f"Error generating embedding with OpenAI, falling back to local model: {e}")
            return self.embedding_model.encode(text)
    
    def _extract_page_numbers(self, chunk: str, content: Dict[str, Any]) -> List[int]:
        """Extract page numbers that this chunk might belong to."""
        # Simple heuristic - could be improved with more sophisticated mapping
        pages = content.get("pages", [])
        if not pages:
            return []
        
        # Find pages that contain parts of this chunk
        matching_pages = []
        for page in pages:
            page_text = page.get("text", "")
            if any(word in page_text for word in chunk.split()[:10]):  # Check first 10 words
                matching_pages.append(page.get("page_number", 0))
        
        return matching_pages
    
    async def _analyze_brand_elements(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze brand elements using Claude."""
        try:
            text_content = content.get("text", "")
            brand_elements = content.get("brand_elements", {})
            
            prompt = f"""
            Analyze the following brand playbook content and extract key brand elements:

            Content:
            {text_content[:5000]}  # Limit content for API call

            Existing extracted elements:
            {json.dumps(brand_elements, indent=2)}

            Please provide a comprehensive analysis including:
            1. Brand identity elements (colors, fonts, logos)
            2. Brand voice and tone characteristics
            3. Key brand messages and positioning
            4. Brand guidelines and rules
            5. Target audience insights
            6. Brand values and personality traits

            Format your response as a structured JSON object.
            """
            
            response = await self.anthropic_client.messages.create(
                model=settings.ANTHROPIC_MODEL,
                max_tokens=2000,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Parse Claude's response
            analysis_text = response.content[0].text
            
            # Try to extract JSON from response
            try:
                # Look for JSON in the response
                import re
                json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
                if json_match:
                    analysis = json.loads(json_match.group())
                else:
                    # Fallback to structured text analysis
                    analysis = {"raw_analysis": analysis_text}
            except json.JSONDecodeError:
                analysis = {"raw_analysis": analysis_text}
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing brand elements: {e}")
            return {"error": str(e)}
    
    async def answer_question(
        self,
        question: str,
        document_ids: List[UUID],
        user_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Answer a question using RAG with document content.
        
        Args:
            question: User's question
            document_ids: List of document IDs to search
            user_context: Additional user context
            
        Returns:
            Answer with sources and confidence score
        """
        try:
            # Generate embedding for the question
            question_embedding = await self._generate_embedding(question)
            
            # Retrieve relevant chunks
            relevant_chunks = await self._retrieve_relevant_chunks(
                question_embedding,
                document_ids,
                top_k=5
            )
            
            if not relevant_chunks:
                return {
                    "answer": "I couldn't find relevant information in the provided documents to answer your question.",
                    "confidence": 0.0,
                    "sources": [],
                }
            
            # Prepare context from relevant chunks
            context = "\n\n".join([
                f"Source {i+1}: {chunk['text']}"
                for i, chunk in enumerate(relevant_chunks)
            ])
            
            # Generate answer using Claude
            prompt = f"""
            You are an expert brand consultant analyzing brand playbooks. Answer the following question based on the provided context from brand documents.

            Question: {question}

            Context from brand documents:
            {context}

            Please provide:
            1. A comprehensive answer based on the context
            2. Specific references to the source material
            3. If the context doesn't fully answer the question, clearly state what information is missing

            Be precise and cite specific passages when possible.
            """
            
            response = await self.anthropic_client.messages.create(
                model=settings.ANTHROPIC_MODEL,
                max_tokens=1500,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            answer = response.content[0].text
            
            # Calculate confidence based on relevance scores
            avg_relevance = np.mean([chunk['relevance_score'] for chunk in relevant_chunks])
            confidence = min(avg_relevance * 1.2, 1.0)  # Scale and cap at 1.0
            
            # Prepare sources
            sources = [
                {
                    "document_id": chunk["document_id"],
                    "text": chunk["text"][:200] + "..." if len(chunk["text"]) > 200 else chunk["text"],
                    "relevance_score": chunk["relevance_score"],
                    "page_numbers": chunk.get("metadata", {}).get("page_numbers", []),
                }
                for chunk in relevant_chunks
            ]
            
            return {
                "answer": answer,
                "confidence": confidence,
                "sources": sources,
                "question": question,
            }
            
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return {
                "answer": "I encountered an error while processing your question. Please try again.",
                "confidence": 0.0,
                "sources": [],
                "error": str(e),
            }
    
    async def _retrieve_relevant_chunks(
        self,
        query_embedding: np.ndarray,
        document_ids: List[UUID],
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant chunks using vector similarity."""
        try:
            # Query MongoDB for document chunks
            collection = self.mongodb["document_embeddings"]
            
            # Get all chunks for the specified documents
            chunks = await collection.find({
                "document_id": {"$in": [str(doc_id) for doc_id in document_ids]}
            }).to_list(length=None)
            
            if not chunks:
                return []
            
            # Calculate similarity scores
            chunk_scores = []
            for chunk in chunks:
                chunk_embedding = np.array(chunk["embedding"])
                
                # Calculate cosine similarity
                similarity = np.dot(query_embedding, chunk_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(chunk_embedding)
                )
                
                chunk_scores.append({
                    **chunk,
                    "relevance_score": float(similarity)
                })
            
            # Sort by relevance and return top_k
            chunk_scores.sort(key=lambda x: x["relevance_score"], reverse=True)
            return chunk_scores[:top_k]
            
        except Exception as e:
            logger.error(f"Error retrieving relevant chunks: {e}")
            return []
