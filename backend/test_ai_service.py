#!/usr/bin/env python3
"""
Test script for AI service functionality.
"""
import os
import sys
from typing import Dict, Any, List, Optional
import json

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Import the AI service
    from app.services.ai_service import (
        analyze_resume, 
        analyze_large_resume,
        split_resume_into_sections,
        search_similar_documents
    )
except ImportError as e:
    print(f"Error importing AI service modules: {e}")
    sys.exit(1)

def test_resume_chunking():
    """Test the resume chunking functionality."""
    print("Testing resume chunking...")
    
    # Sample resume text
    sample_resume = """
    John Doe
    Software Engineer
    
    Summary:
    Experienced software engineer with 5+ years of experience in Python, JavaScript, and cloud technologies.
    
    Experience:
    Senior Software Engineer, ABC Tech (2020-Present)
    - Developed and maintained microservices using Python and FastAPI
    - Implemented CI/CD pipelines using GitHub Actions
    - Optimized database queries resulting in 30% performance improvement
    
    Software Engineer, XYZ Corp (2018-2020)
    - Built responsive web applications using React and TypeScript
    - Collaborated with cross-functional teams to deliver features on time
    - Mentored junior developers and conducted code reviews
    
    Education:
    Bachelor of Science in Computer Science, University of Technology (2014-2018)
    
    Skills:
    Python, JavaScript, TypeScript, React, FastAPI, Docker, Kubernetes, AWS, Git
    """
    
    try:
        # Test section splitting
        sections = split_resume_into_sections(sample_resume)
        print(f"Identified {len(sections)} sections:")
        for section, content in sections.items():
            print(f"- {section}: {len(content)} characters")
        
        # Test large resume analysis
        try:
            result = analyze_large_resume(sample_resume)
            print("\nLarge resume analysis result:")
            print(json.dumps(result, indent=2))
        except Exception as e:
            print(f"Error testing large resume analysis: {e}")
            return False
        
        return True
    except Exception as e:
        print(f"Error in test_resume_chunking: {e}")
        return False

def test_search_documents():
    """Test the document search functionality."""
    print("\nTesting document search...")
    
    # Sample query
    query = "Python FastAPI development"
    
    try:
        # Search for documents
        results = search_similar_documents(query, top_k=2)
        print(f"Found {len(results)} results for query: '{query}'")
        
        # Print results
        for i, result in enumerate(results):
            print(f"\nResult {i+1}:")
            try:
                if hasattr(result, 'id'):
                    print(f"ID: {result.id}")
                    print(f"Score: {result.score}")
                    if hasattr(result, 'metadata') and result.metadata:
                        print(f"Metadata: {result.metadata}")
                elif isinstance(result, dict):
                    print(f"ID: {result.get('id', 'unknown')}")
                    print(f"Score: {result.get('score', 0)}")
                    if 'metadata' in result:
                        print(f"Metadata: {result['metadata']}")
            except Exception as e:
                print(f"Error processing result {i+1}: {e}")
        
        return True
    except Exception as e:
        print(f"Error in test_search_documents: {e}")
        return False

if __name__ == "__main__":
    # Set up basic logging
    import logging
    logging.basicConfig(level=logging.INFO, 
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Run tests
    try:
        resume_test_result = test_resume_chunking()
        document_test_result = test_search_documents()
        
        if resume_test_result and document_test_result:
            print("\nAll tests completed successfully!")
            sys.exit(0)
        else:
            print("\nSome tests failed.")
            sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 