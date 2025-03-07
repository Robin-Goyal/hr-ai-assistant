from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Union
from datetime import datetime

# Document schemas
class DocumentBase(BaseModel):
    title: str
    category: str
    offline_available: bool = False

class DocumentCreate(DocumentBase):
    pass

class DocumentResponse(DocumentBase):
    id: int
    file_path: str
    created_at: datetime

    class Config:
        from_attributes = True

# Skill schemas
class SkillBase(BaseModel):
    name: str
    category: Optional[str] = None

class SkillCreate(SkillBase):
    pass

class SkillUpdate(SkillBase):
    name: Optional[str] = None
    category: Optional[str] = None

class Skill(SkillBase):
    id: int
    
    class Config:
        from_attributes = True

class SkillOut(BaseModel):
    id: int
    name: str
    category: Optional[str] = None

    class Config:
        from_attributes = True

class SkillNameList(BaseModel):
    skill_names: List[str]

# Department schemas
class DepartmentBase(BaseModel):
    name: str
    description: Optional[str] = None

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentUpdate(DepartmentBase):
    name: Optional[str] = None
    description: Optional[str] = None

class Department(DepartmentBase):
    id: int
    
    class Config:
        from_attributes = True

# Position schemas
class PositionBase(BaseModel):
    title: str
    description: Optional[str] = None
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    location: Optional[str] = None
    salary_range: Optional[str] = None
    is_active: bool = True
    department_id: int

class PositionCreate(PositionBase):
    pass

class PositionUpdate(PositionBase):
    title: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    location: Optional[str] = None
    salary_range: Optional[str] = None
    is_active: Optional[bool] = None
    department_id: Optional[int] = None

class Position(PositionBase):
    id: int
    created_date: datetime
    updated_date: datetime
    
    class Config:
        from_attributes = True

class PositionDetail(Position):
    department: Department
    
    class Config:
        from_attributes = True

# Candidate schemas
class CandidateBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    position_id: Optional[int] = None
    status: str = "New"

class CandidateCreate(CandidateBase):
    pass

class CandidateUpdate(CandidateBase):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    position_id: Optional[int] = None
    status: Optional[str] = None

class Candidate(CandidateBase):
    id: int
    resume_path: Optional[str] = None
    created_date: datetime
    updated_date: datetime
    skill_match_score: Optional[float] = None
    
    class Config:
        from_attributes = True

class CandidateDetail(Candidate):
    position: Optional[Position] = None
    skills: List[Skill] = []
    
    class Config:
        from_attributes = True

# Application schemas
class ApplicationBase(BaseModel):
    candidate_id: int
    position_id: int
    status: str = "New"
    notes: Optional[str] = None

class ApplicationCreate(ApplicationBase):
    pass

class ApplicationUpdate(ApplicationBase):
    candidate_id: Optional[int] = None
    position_id: Optional[int] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    interview_date: Optional[datetime] = None

class Application(ApplicationBase):
    id: int
    applied_date: datetime
    status_updated_date: datetime
    interview_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ApplicationDetail(Application):
    candidate: Candidate
    position: Position
    
    class Config:
        from_attributes = True

# Note schemas
class NoteBase(BaseModel):
    candidate_id: int
    content: str
    note_type: str = "General"
    created_by: Optional[str] = None

class NoteCreate(NoteBase):
    pass

class NoteUpdate(NoteBase):
    candidate_id: Optional[int] = None
    content: Optional[str] = None
    note_type: Optional[str] = None
    created_by: Optional[str] = None

class Note(NoteBase):
    id: int
    created_date: datetime
    updated_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None

class User(UserBase):
    id: int
    created_date: datetime
    
    class Config:
        from_attributes = True

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: str
    exp: int

# Question template schemas
class QuestionTemplateBase(BaseModel):
    content: str
    difficulty: str = "Medium"
    category: str

class QuestionTemplateCreate(QuestionTemplateBase):
    pass

class QuestionTemplate(QuestionTemplateBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Question set schemas
class QuestionSetBase(BaseModel):
    name: str
    description: Optional[str] = None
    template_id: Optional[int] = None

class QuestionSetCreate(QuestionSetBase):
    pass

class QuestionSet(QuestionSetBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Question schemas
class QuestionBase(BaseModel):
    content: str
    difficulty: str = "Medium"
    category: str
    question_set_id: Optional[int] = None

class QuestionCreate(QuestionBase):
    pass

class Question(QuestionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Interview schemas
class InterviewBase(BaseModel):
    candidate_id: int
    question_set_id: Optional[int] = None
    scheduled_date: Optional[datetime] = None
    status: str = "Scheduled"
    notes: Optional[str] = None

class InterviewCreate(InterviewBase):
    pass

class Interview(InterviewBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Chat message schemas
class ChatMessageBase(BaseModel):
    content: str
    is_user: bool = True
    conversation_id: str
    saved: bool = False

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessage(ChatMessageBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# For document upload
class DocumentUpload(BaseModel):
    title: str
    category: str
    offline_available: bool = False

# For resume analysis
class ResumeAnalysisRequest(BaseModel):
    candidate_id: int

class ResumeAnalysisResponse(BaseModel):
    skills: List[str]
    experience_years: float
    education: str
    summary: str
    match_score: Optional[float] = None

# For question generation
class QuestionGenerationRequest(BaseModel):
    position_id: int
    difficulty: str = "Medium"
    count: int = 5
    categories: List[str] = []

class QuestionGenerationResponse(BaseModel):
    questions: List[Question]

# For chat
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    message: str
    conversation_id: str 