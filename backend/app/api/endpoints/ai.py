from typing import Any, List, Optional
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from ...db.database import get_db
from ...models.models import Position, Candidate, ChatMessage, User
from ...services import ai_service, document_service
from ...services.auth_service import get_current_active_user
from ...models.schemas import (
    ChatRequest, ChatResponse, 
    QuestionGenerationRequest, QuestionGenerationResponse,
    ResumeAnalysisRequest, ResumeAnalysisResponse
)

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Chat with the AI assistant."""
    try:
        # Generate or use existing conversation ID
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        # Store the user message
        db_message = ChatMessage(
            content=request.message,
            is_user=True,
            conversation_id=conversation_id
        )
        db.add(db_message)
        db.commit()
        
        # Implement RAG: Search for relevant documents
        relevant_docs = document_service.search_documents(request.message, top_k=3)
        
        # Extract relevant sections from the documents to avoid context length issues
        context, sources = document_service.extract_relevant_sections(request.message, relevant_docs)

        print(f"context: {context}")
        
        # Generate AI response with context
        response_text = ai_service.generate_ai_response(request.message, context)
        
        # If we have sources, append them to the response
        if sources and len(sources) > 0:
            response_text += "\n\nSources: " + ", ".join(sources)
        
        # Store the AI response
        db_response = ChatMessage(
            content=response_text,
            is_user=False,
            conversation_id=conversation_id
        )
        db.add(db_response)
        db.commit()
        
        return {
            "message": response_text,
            "conversation_id": conversation_id
        }
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat request: {str(e)}"
        )

@router.post("/questions", response_model=QuestionGenerationResponse)
async def generate_questions(
    request: QuestionGenerationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Generate interview questions based on position requirements."""
    try:
        # Get position details
        position = db.query(Position).filter(Position.id == request.position_id).first()
        if not position:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Position not found"
            )
            
        # Generate questions based on position description and specified criteria
        position_description = position.description or ""
        if position.requirements:
            position_description += "\n\nRequirements:\n" + position.requirements
            
        if position.responsibilities:
            position_description += "\n\nResponsibilities:\n" + position.responsibilities
            
        questions = ai_service.generate_interview_questions(
            position_description,
            request.difficulty,
            request.count,
            request.categories
        )
        
        # Convert string questions to proper Question objects
        question_objects = []
        for i, question_text in enumerate(questions):
            question = {
                "id": i + 1,
                "content": question_text,
                "difficulty": request.difficulty,
                "category": request.categories[0] if request.categories else "General",
                "created_at": datetime.now()
            }
            question_objects.append(question)
            
        return {"questions": question_objects}
    except Exception as e:
        print(f"Error generating questions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating questions: {str(e)}"
        )

@router.post("/resume-analysis", response_model=ResumeAnalysisResponse)
async def analyze_resume(
    request: ResumeAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Analyze a candidate's resume."""
    try:
        # Get candidate details
        candidate = db.query(Candidate).filter(Candidate.id == request.candidate_id).first()
        if not candidate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Candidate not found"
            )
        
        if not candidate.resume_content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Candidate has no resume content to analyze"
            )
        
        # Get position details if provided
        position_description = None
        if candidate.position_id:
            position = db.query(Position).filter(Position.id == candidate.position_id).first()
            if position:
                position_description = position.description
        
        # Analyze resume - this now handles large resumes internally
        analysis = ai_service.analyze_resume(candidate.resume_content, position_description)
        
        # Update candidate's skill match score if available
        if "match_score" in analysis and analysis["match_score"] is not None:
            candidate.skill_match_score = analysis["match_score"]
            db.commit()
        
        # Ensure the response matches the expected schema
        if not isinstance(analysis["skills"], list):
            analysis["skills"] = []
        
        if "experience_years" not in analysis or analysis["experience_years"] is None:
            analysis["experience_years"] = 0
            
        # Convert experience_years to float if it's not already
        try:
            analysis["experience_years"] = float(analysis["experience_years"])
        except (ValueError, TypeError):
            analysis["experience_years"] = 0
            
        if "education" not in analysis or not analysis["education"]:
            analysis["education"] = "Not specified"
            
        if "summary" not in analysis or not analysis["summary"]:
            analysis["summary"] = "No summary available"
            
        return analysis
    except Exception as e:
        print(f"Error analyzing resume: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing resume: {str(e)}"
        ) 