#!/usr/bin/env python3
"""
Test script for document service functionality.
"""
import os
import sys
from typing import Dict, Any, List, Optional

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the document service
from app.services.document_service import chunk_text, search_documents

def test_text_chunking():
    """Test the text chunking functionality."""
    print("Testing text chunking...")
    
    # Sample text
    sample_text = """
    FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.6+ based on standard Python type hints.
    
    The key features are:
    
    Fast: Very high performance, on par with NodeJS and Go (thanks to Starlette and Pydantic). One of the fastest Python frameworks available.
    
    Fast to code: Increase the speed to develop features by about 200% to 300%. *
    
    Fewer bugs: Reduce about 40% of human (developer) induced errors. *
    
    Intuitive: Great editor support. Completion everywhere. Less time debugging.
    
    Easy: Designed to be easy to use and learn. Less time reading docs.
    
    Short: Minimize code duplication. Multiple features from each parameter declaration. Fewer bugs.
    
    Robust: Get production-ready code. With automatic interactive documentation.
    
    Standards-based: Based on (and fully compatible with) the open standards for APIs: OpenAPI (previously known as Swagger) and JSON Schema.
    
    * estimation based on tests on an internal development team, building production applications.
    """
    
    # Test chunking with different sizes
    chunks_small = chunk_text(sample_text, chunk_size=200, overlap=50)
    print(f"Small chunks (size=200, overlap=50): {len(chunks_small)} chunks")
    for i, chunk in enumerate(chunks_small):
        print(f"- Chunk {i+1}: {len(chunk)} characters")
    
    chunks_medium = chunk_text(sample_text, chunk_size=500, overlap=100)
    print(f"\nMedium chunks (size=500, overlap=100): {len(chunks_medium)} chunks")
    for i, chunk in enumerate(chunks_medium):
        print(f"- Chunk {i+1}: {len(chunk)} characters")
    
    return True

def test_document_search():
    """Test the document search functionality."""
    print("\nTesting document search...")
    
    # Sample query
    query = "FastAPI performance"
    
    # Search for documents
    results = search_documents(query, top_k=2)
    print(f"Found {len(results)} results for query: '{query}'")
    
    # Print results
    for i, result in enumerate(results):
        print(f"\nResult {i+1}:")
        if hasattr(result, 'id'):
            print(f"ID: {result.id}")
            print(f"Score: {result.score}")
            if hasattr(result, 'metadata') and result.metadata:
                print(f"Metadata keys: {list(result.metadata.keys())}")
                if 'text' in result.metadata:
                    text_preview = result.metadata['text'][:100] + "..." if len(result.metadata['text']) > 100 else result.metadata['text']
                    print(f"Text preview: {text_preview}")
        elif isinstance(result, dict):
            print(f"ID: {result.get('id', 'unknown')}")
            print(f"Score: {result.get('score', 0)}")
            if 'metadata' in result:
                print(f"Metadata keys: {list(result['metadata'].keys())}")
                if 'text' in result['metadata']:
                    text_preview = result['metadata']['text'][:100] + "..." if len(result['metadata']['text']) > 100 else result['metadata']['text']
                    print(f"Text preview: {text_preview}")
    
    return True

if __name__ == "__main__":
    # Run tests
    try:
        test_text_chunking()
        test_document_search()
        print("\nAll tests completed successfully!")
    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 