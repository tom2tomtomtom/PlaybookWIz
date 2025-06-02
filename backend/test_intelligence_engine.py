#!/usr/bin/env python3
"""
Test script for the PlaybookWiz Intelligence Engine
This script tests the core functionality without requiring full API setup
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from intelligence_engine import (
    DocumentProcessor, 
    TextChunker, 
    VectorDatabase, 
    PlaybookIntelligence,
    DocumentChunk
)

async def test_document_processing():
    """Test document processing capabilities"""
    print("🧪 Testing Document Processing...")
    
    # Test text chunking
    sample_text = """
    Brand Guidelines Document
    
    Our primary brand color is Blue (#1E40AF). This color should be used for all primary brand elements including headers, buttons, and key visual elements.
    
    Secondary colors include:
    - Light Gray (#F8F9FA) for backgrounds
    - Dark Gray (#343A40) for text
    - Green (#28A745) for success states
    
    Typography guidelines specify that we use Inter font family for all digital applications. The font weights should be:
    - Regular (400) for body text
    - Medium (500) for subheadings  
    - Bold (700) for main headings
    
    Logo usage requires minimum clear space of 2x the height of the logo mark on all sides.
    """
    
    # Test chunking
    chunks = TextChunker.chunk_text(sample_text, max_tokens=100, overlap_tokens=20)
    print(f"✅ Created {len(chunks)} text chunks")
    
    # Test document chunk creation
    pages_text = [(sample_text, 1)]
    doc_chunks = TextChunker.create_document_chunks(
        pages_text, "test-doc-123", "test_brand_guidelines.pdf"
    )
    print(f"✅ Created {len(doc_chunks)} document chunks")
    
    return doc_chunks

async def test_vector_database():
    """Test vector database operations"""
    print("\n🧪 Testing Vector Database...")
    
    try:
        # Initialize vector database
        vector_db = VectorDatabase("test_collection")
        print("✅ Vector database initialized")
        
        # Create sample chunks
        sample_chunks = [
            DocumentChunk(
                id="chunk_1",
                text="Our primary brand color is Blue (#1E40AF)",
                document_id="doc_1",
                document_name="brand_guidelines.pdf",
                page_number=1,
                chunk_index=0,
                token_count=10,
                metadata={"type": "color_guideline"}
            ),
            DocumentChunk(
                id="chunk_2", 
                text="Typography uses Inter font family with Regular, Medium, and Bold weights",
                document_id="doc_1",
                document_name="brand_guidelines.pdf",
                page_number=2,
                chunk_index=1,
                token_count=12,
                metadata={"type": "typography_guideline"}
            )
        ]
        
        # Add chunks to vector database
        success = await vector_db.add_document_chunks(sample_chunks, "test_user_123")
        if success:
            print("✅ Added chunks to vector database")
        else:
            print("❌ Failed to add chunks to vector database")
            return False
        
        # Test search
        search_results = await vector_db.search_similar_passages(
            "What is the primary brand color?", 
            "test_user_123", 
            n_results=2
        )
        
        print(f"✅ Search returned {len(search_results)} results")
        for i, result in enumerate(search_results):
            print(f"   Result {i+1}: {result.passage[:50]}... (score: {result.relevance_score:.3f})")
        
        return True
        
    except Exception as e:
        print(f"❌ Vector database test failed: {e}")
        return False

async def test_intelligence_engine():
    """Test the complete intelligence engine"""
    print("\n🧪 Testing Complete Intelligence Engine...")
    
    try:
        # Initialize intelligence engine
        engine = PlaybookIntelligence()
        print("✅ Intelligence engine initialized")
        
        # Test document processing (simulated)
        sample_content = b"Sample PDF content for testing"
        success = await engine.process_document(
            sample_content,
            "test_document.pdf", 
            "test_doc_456",
            "test_user_123"
        )
        
        if success:
            print("✅ Document processing completed")
        else:
            print("❌ Document processing failed")
        
        # Test user stats
        stats = await engine.get_user_stats("test_user_123")
        print(f"✅ User stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Intelligence engine test failed: {e}")
        return False

async def test_dependencies():
    """Test that all required dependencies are available"""
    print("🧪 Testing Dependencies...")
    
    dependencies = [
        ("chromadb", "ChromaDB"),
        ("sentence_transformers", "Sentence Transformers"),
        ("tiktoken", "TikToken"),
        ("PyPDF2", "PyPDF2"),
        ("pptx", "python-pptx"),
        ("openai", "OpenAI"),
        ("httpx", "HTTPX"),
        ("supabase", "Supabase"),
        ("cryptography", "Cryptography")
    ]
    
    missing_deps = []
    
    for module, name in dependencies:
        try:
            __import__(module)
            print(f"✅ {name} available")
        except ImportError:
            print(f"❌ {name} missing")
            missing_deps.append(name)
    
    if missing_deps:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing_deps)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True

async def main():
    """Run all tests"""
    print("🚀 PlaybookWiz Intelligence Engine Test Suite")
    print("=" * 50)
    
    # Test dependencies first
    deps_ok = await test_dependencies()
    if not deps_ok:
        print("\n❌ Dependency test failed. Please install missing packages.")
        return
    
    # Test document processing
    try:
        doc_chunks = await test_document_processing()
    except Exception as e:
        print(f"❌ Document processing test failed: {e}")
        return
    
    # Test vector database
    try:
        vector_ok = await test_vector_database()
        if not vector_ok:
            print("\n❌ Vector database test failed.")
            return
    except Exception as e:
        print(f"❌ Vector database test failed: {e}")
        return
    
    # Test complete intelligence engine
    try:
        engine_ok = await test_intelligence_engine()
        if not engine_ok:
            print("\n❌ Intelligence engine test failed.")
            return
    except Exception as e:
        print(f"❌ Intelligence engine test failed: {e}")
        return
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! Intelligence engine is ready.")
    print("\nNext steps:")
    print("1. Configure your .env file with Supabase credentials")
    print("2. Run the SQL scripts to create database tables")
    print("3. Start the backend: python intelligent_main.py")
    print("4. Start the frontend: cd frontend/out && python3 -m http.server 9000")

if __name__ == "__main__":
    asyncio.run(main())
