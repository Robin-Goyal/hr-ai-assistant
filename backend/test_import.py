#!/usr/bin/env python
"""
Test script to verify imports are working correctly.
"""
import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test that all necessary imports are working."""
    try:
        from app.services.auth_service import get_current_active_user
        print("✅ Successfully imported auth_service.get_current_active_user")
    except ImportError as e:
        print(f"❌ Failed to import auth_service.get_current_active_user: {e}")
        
    try:
        from app.api.endpoints.ai import router as ai_router
        print("✅ Successfully imported ai.router")
    except ImportError as e:
        print(f"❌ Failed to import ai.router: {e}")
        
    try:
        from app.services.ai_service import analyze_resume
        print("✅ Successfully imported ai_service.analyze_resume")
    except ImportError as e:
        print(f"❌ Failed to import ai_service.analyze_resume: {e}")
        
    try:
        from app.services.document_service import search_documents
        print("✅ Successfully imported document_service.search_documents")
    except ImportError as e:
        print(f"❌ Failed to import document_service.search_documents: {e}")
        
    print("\nImport test completed.")

if __name__ == "__main__":
    test_imports() 