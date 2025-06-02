"""
Brand Playbook Intelligence Engine
Complete vector-based semantic search and passage retrieval system
"""

import logging
import os
import uuid
import asyncio
from typing import List, Dict, Any, Optional, Tuple
import chromadb
from chromadb.config import Settings
import openai
import tiktoken
from sentence_transformers import SentenceTransformer
import PyPDF2
from pptx import Presentation
import io
import re
from dataclasses import dataclass
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize clients
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(
    path="./chroma_db",
    settings=Settings(
        anonymized_telemetry=False,
        allow_reset=True
    )
)

# Initialize embedding model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize tokenizer for text chunking
tokenizer = tiktoken.get_encoding("cl100k_base")

@dataclass
class DocumentChunk:
    """Represents a chunk of text from a document"""
    id: str
    text: str
    document_id: str
    document_name: str
    page_number: int
    chunk_index: int
    token_count: int
    metadata: Dict[str, Any]

@dataclass
class SearchResult:
    """Represents a search result with source attribution"""
    passage: str
    document_name: str
    page_number: int
    relevance_score: float
    document_id: str
    chunk_id: str

@dataclass
class IntelligentResponse:
    """Complete AI response with sources and confidence"""
    answer: str
    confidence: float
    sources: List[SearchResult]
    query: str
    processing_time: float

class DocumentProcessor:
    """Handles document processing and text extraction"""
    
    @staticmethod
    async def extract_pdf_text_with_pages(content: bytes) -> List[Tuple[str, int]]:
        """Extract text from PDF with page numbers"""
        try:
            pdf_file = io.BytesIO(content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            pages_text = []
            
            for page_num, page in enumerate(pdf_reader.pages, 1):
                text = page.extract_text()
                if text.strip():  # Only add non-empty pages
                    pages_text.append((text.strip(), page_num))
            
            return pages_text
        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
            return [("Error extracting PDF text", 1)]
    
    @staticmethod
    async def extract_ppt_text_with_slides(content: bytes) -> List[Tuple[str, int]]:
        """Extract text from PowerPoint with slide numbers"""
        try:
            ppt_file = io.BytesIO(content)
            presentation = Presentation(ppt_file)
            slides_text = []
            
            for slide_num, slide in enumerate(presentation.slides, 1):
                slide_text = ""
                for shape in slide.shapes:
                    if hasattr(shape, "text") and shape.text.strip():
                        slide_text += shape.text + "\n"
                
                if slide_text.strip():  # Only add non-empty slides
                    slides_text.append((slide_text.strip(), slide_num))
            
            return slides_text
        except Exception as e:
            logger.error(f"PPT extraction error: {e}")
            return [("Error extracting PowerPoint text", 1)]

class TextChunker:
    """Handles intelligent text chunking with overlap"""
    
    @staticmethod
    def chunk_text(text: str, max_tokens: int = 500, overlap_tokens: int = 50) -> List[str]:
        """Split text into overlapping chunks"""
        tokens = tokenizer.encode(text)
        chunks = []
        
        start = 0
        while start < len(tokens):
            end = min(start + max_tokens, len(tokens))
            chunk_tokens = tokens[start:end]
            chunk_text = tokenizer.decode(chunk_tokens)
            chunks.append(chunk_text)
            
            if end >= len(tokens):
                break
            
            start = end - overlap_tokens
        
        return chunks
    
    @staticmethod
    def create_document_chunks(
        pages_text: List[Tuple[str, int]], 
        document_id: str, 
        document_name: str
    ) -> List[DocumentChunk]:
        """Create document chunks with metadata"""
        chunks = []
        chunk_index = 0
        
        for text, page_number in pages_text:
            # Split page text into chunks
            page_chunks = TextChunker.chunk_text(text)
            
            for chunk_text in page_chunks:
                chunk_id = f"{document_id}_chunk_{chunk_index}"
                token_count = len(tokenizer.encode(chunk_text))
                
                chunk = DocumentChunk(
                    id=chunk_id,
                    text=chunk_text,
                    document_id=document_id,
                    document_name=document_name,
                    page_number=page_number,
                    chunk_index=chunk_index,
                    token_count=token_count,
                    metadata={
                        "document_type": "pdf" if document_name.endswith('.pdf') else "ppt",
                        "created_at": str(uuid.uuid4())
                    }
                )
                chunks.append(chunk)
                chunk_index += 1
        
        return chunks

class VectorDatabase:
    """Manages ChromaDB operations"""
    
    def __init__(self, collection_name: str = "brand_playbooks"):
        self.collection_name = collection_name
        self.collection = None
        self._initialize_collection()
    
    def _initialize_collection(self):
        """Initialize or get existing collection"""
        try:
            self.collection = chroma_client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Brand playbook document chunks"}
            )
            logger.info(f"Initialized collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error initializing collection: {e}")
            raise
    
    async def add_document_chunks(self, chunks: List[DocumentChunk], user_id: str):
        """Add document chunks to vector database"""
        try:
            # Prepare data for ChromaDB
            ids = [chunk.id for chunk in chunks]
            documents = [chunk.text for chunk in chunks]
            metadatas = []
            
            for chunk in chunks:
                metadata = {
                    "document_id": chunk.document_id,
                    "document_name": chunk.document_name,
                    "page_number": chunk.page_number,
                    "chunk_index": chunk.chunk_index,
                    "token_count": chunk.token_count,
                    "user_id": user_id,
                    **chunk.metadata
                }
                metadatas.append(metadata)
            
            # Generate embeddings
            embeddings = embedding_model.encode(documents).tolist()
            
            # Add to ChromaDB
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings
            )
            
            logger.info(f"Added {len(chunks)} chunks to vector database")
            return True
            
        except Exception as e:
            logger.error(f"Error adding chunks to vector database: {e}")
            return False
    
    async def search_similar_passages(
        self, 
        query: str, 
        user_id: str, 
        n_results: int = 5,
        document_ids: Optional[List[str]] = None
    ) -> List[SearchResult]:
        """Search for similar passages using vector similarity"""
        try:
            # Generate query embedding
            query_embedding = embedding_model.encode([query]).tolist()[0]
            
            # Prepare where clause for user filtering
            where_clause = {"user_id": user_id}
            if document_ids:
                where_clause["document_id"] = {"$in": document_ids}
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_clause,
                include=["documents", "metadatas", "distances"]
            )
            
            # Convert to SearchResult objects
            search_results = []
            if results['documents'] and results['documents'][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                )):
                    # Convert distance to similarity score (0-1)
                    relevance_score = max(0, 1 - distance)
                    
                    search_result = SearchResult(
                        passage=doc,
                        document_name=metadata['document_name'],
                        page_number=metadata['page_number'],
                        relevance_score=relevance_score,
                        document_id=metadata['document_id'],
                        chunk_id=metadata.get('chunk_id', f"chunk_{i}")
                    )
                    search_results.append(search_result)
            
            return search_results
            
        except Exception as e:
            logger.error(f"Error searching vector database: {e}")
            return []
    
    async def get_user_document_count(self, user_id: str) -> int:
        """Get count of documents for a user"""
        try:
            results = self.collection.get(
                where={"user_id": user_id},
                include=["metadatas"]
            )
            
            # Count unique documents
            document_ids = set()
            if results['metadatas']:
                for metadata in results['metadatas']:
                    document_ids.add(metadata['document_id'])
            
            return len(document_ids)
            
        except Exception as e:
            logger.error(f"Error getting document count: {e}")
            return 0
    
    async def delete_document_chunks(self, document_id: str, user_id: str):
        """Delete all chunks for a document"""
        try:
            self.collection.delete(
                where={
                    "document_id": document_id,
                    "user_id": user_id
                }
            )
            logger.info(f"Deleted chunks for document: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document chunks: {e}")
            return False

class AIResponseGenerator:
    """Generates intelligent responses using retrieved passages"""

    @staticmethod
    async def generate_response(
        query: str,
        search_results: List[SearchResult],
        api_key: str,
        provider: str = "openai"
    ) -> IntelligentResponse:
        """Generate AI response with source attribution"""
        import time
        start_time = time.time()

        try:
            # Prepare context from search results
            context_passages = []
            for i, result in enumerate(search_results[:3], 1):  # Use top 3 results
                context_passages.append(
                    f"Source {i} (from {result.document_name}, page {result.page_number}):\n{result.passage}\n"
                )

            context = "\n".join(context_passages)

            # Create prompt for AI
            system_prompt = """You are a helpful brand expert assistant. Answer questions based ONLY on the provided brand playbook content.

Rules:
1. Use only information from the provided sources
2. Be specific and accurate
3. If information isn't in the sources, say so
4. Reference specific sources when possible
5. Keep answers concise but complete"""

            user_prompt = f"""Context from brand playbooks:
{context}

Question: {query}

Please provide a helpful answer based on the brand playbook information above."""

            # Generate response based on provider
            if provider == "openai":
                response_text = await AIResponseGenerator._call_openai(
                    system_prompt, user_prompt, api_key
                )
            else:  # claude
                response_text = await AIResponseGenerator._call_claude(
                    system_prompt, user_prompt, api_key
                )

            # Calculate confidence based on relevance scores
            if search_results:
                avg_relevance = sum(r.relevance_score for r in search_results) / len(search_results)
                confidence = min(0.95, avg_relevance * 1.2)  # Cap at 95%
            else:
                confidence = 0.1

            processing_time = time.time() - start_time

            return IntelligentResponse(
                answer=response_text,
                confidence=confidence,
                sources=search_results,
                query=query,
                processing_time=processing_time
            )

        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            processing_time = time.time() - start_time

            return IntelligentResponse(
                answer=f"I apologize, but I encountered an error while processing your question: {str(e)}",
                confidence=0.0,
                sources=search_results,
                query=query,
                processing_time=processing_time
            )

    @staticmethod
    async def _call_openai(system_prompt: str, user_prompt: str, api_key: str) -> str:
        """Call OpenAI API"""
        try:
            client = openai.AsyncOpenAI(api_key=api_key)

            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return f"Error calling OpenAI API: {str(e)}"

    @staticmethod
    async def _call_claude(system_prompt: str, user_prompt: str, api_key: str) -> str:
        """Call Claude API"""
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": api_key,
                        "Content-Type": "application/json",
                        "anthropic-version": "2023-06-01"
                    },
                    json={
                        "model": "claude-3-sonnet-20240229",
                        "max_tokens": 500,
                        "messages": [
                            {"role": "user", "content": f"{system_prompt}\n\n{user_prompt}"}
                        ]
                    },
                    timeout=30.0
                )

                if response.status_code == 200:
                    return response.json()["content"][0]["text"]
                else:
                    return f"Claude API error: {response.status_code}"

        except Exception as e:
            logger.error(f"Claude API error: {e}")
            return f"Error calling Claude API: {str(e)}"

class PlaybookIntelligence:
    """Main intelligence engine orchestrator"""

    def __init__(self):
        self.vector_db = VectorDatabase()
        self.document_processor = DocumentProcessor()
        self.text_chunker = TextChunker()
        self.ai_generator = AIResponseGenerator()

    async def process_document(
        self,
        content: bytes,
        filename: str,
        document_id: str,
        user_id: str
    ) -> bool:
        """Complete document processing pipeline"""
        try:
            logger.info(f"Processing document: {filename}")

            # Extract text with page/slide numbers
            if filename.lower().endswith('.pdf'):
                pages_text = await self.document_processor.extract_pdf_text_with_pages(content)
            else:  # PowerPoint
                pages_text = await self.document_processor.extract_ppt_text_with_slides(content)

            # Create chunks
            chunks = self.text_chunker.create_document_chunks(
                pages_text, document_id, filename
            )

            # Store in vector database
            success = await self.vector_db.add_document_chunks(chunks, user_id)

            if success:
                logger.info(f"Successfully processed {len(chunks)} chunks from {filename}")
                return True
            else:
                logger.error(f"Failed to store chunks for {filename}")
                return False

        except Exception as e:
            logger.error(f"Error processing document {filename}: {e}")
            return False

    async def answer_question(
        self,
        query: str,
        user_id: str,
        api_key: str,
        provider: str = "openai",
        document_ids: Optional[List[str]] = None
    ) -> IntelligentResponse:
        """Answer question using intelligent search and AI"""
        try:
            logger.info(f"Processing query: {query}")

            # Search for relevant passages
            search_results = await self.vector_db.search_similar_passages(
                query, user_id, n_results=5, document_ids=document_ids
            )

            if not search_results:
                return IntelligentResponse(
                    answer="I couldn't find any relevant information in your uploaded brand playbooks to answer this question. Please make sure you have uploaded your brand documents first.",
                    confidence=0.0,
                    sources=[],
                    query=query,
                    processing_time=0.0
                )

            # Generate AI response
            response = await self.ai_generator.generate_response(
                query, search_results, api_key, provider
            )

            return response

        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return IntelligentResponse(
                answer=f"I encountered an error while processing your question: {str(e)}",
                confidence=0.0,
                sources=[],
                query=query,
                processing_time=0.0
            )

    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user statistics"""
        try:
            document_count = await self.vector_db.get_user_document_count(user_id)

            return {
                "documents_processed": document_count,
                "vector_database_status": "active",
                "embedding_model": "all-MiniLM-L6-v2"
            }

        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return {
                "documents_processed": 0,
                "vector_database_status": "error",
                "embedding_model": "unknown"
            }

# Initialize global intelligence engine
intelligence_engine = PlaybookIntelligence()
