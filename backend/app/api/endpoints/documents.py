from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
import shutil
from pathlib import Path

from ...db.database import get_db
from ...models.models import User, Document
from ...models.schemas import DocumentCreate, DocumentResponse
from ...services.auth_service import get_current_active_user
from ...services.document_service import create_document, get_document, get_documents, delete_document
from ...core.config import DOCUMENT_DIR

router = APIRouter()

@router.get("/", response_model=List[DocumentResponse])
def read_documents(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Retrieve documents.
    """
    return get_documents(db, skip=skip, limit=limit)

@router.post("/", response_model=DocumentResponse)
async def upload_document(
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
    title: str = Form(...),
    category: str = Form("General"),
    offline_available: bool = Form(False),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Upload a new document.
    """
    # Create directory if it doesn't exist
    os.makedirs(DOCUMENT_DIR, exist_ok=True)
    
    # Create document data
    document_data = DocumentCreate(
        title=title,
        category=category,
        offline_available=offline_available
    )
    
    # Use the document service to create the document
    return await create_document(db, file, document_data)

@router.get("/{document_id}", response_model=DocumentResponse)
def read_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get document by ID.
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@router.delete("/{document_id}", response_model=DocumentResponse)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Delete a document.
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete the file if it exists
    if document.file_path and os.path.exists(document.file_path):
        os.remove(document.file_path)
    
    # Delete the database record
    db.delete(document)
    db.commit()
    
    return document

@router.get("/{document_id}/download")
def download_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Download a document.
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if not document.file_path or not os.path.exists(document.file_path):
        raise HTTPException(status_code=404, detail="Document file not found")
    
    return FileResponse(
        path=document.file_path,
        filename=os.path.basename(document.file_path),
        media_type="application/octet-stream"
    )

@router.get("/{document_id}/view")
def view_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    View a document in the browser.
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if not document.file_path or not os.path.exists(document.file_path):
        raise HTTPException(status_code=404, detail="Document file not found")
    
    # Determine content type based on file extension
    file_extension = document.file_path.split(".")[-1].lower() if "." in document.file_path else ""
    content_type = "application/octet-stream"  # Default
    
    if file_extension in ["pdf"]:
        content_type = "application/pdf"
    elif file_extension in ["jpg", "jpeg"]:
        content_type = "image/jpeg"
    elif file_extension in ["png"]:
        content_type = "image/png"
    elif file_extension in ["txt"]:
        content_type = "text/plain"
    elif file_extension in ["doc", "docx"]:
        content_type = "application/msword"
    
    return FileResponse(
        path=document.file_path,
        media_type=content_type
    ) 