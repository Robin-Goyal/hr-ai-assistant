from datetime import datetime
from typing import List
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Table, DateTime, Float
from sqlalchemy.orm import relationship

from ..db.database import Base

# Association table for position-skill relationship
position_skill = Table(
    "position_skill",
    Base.metadata,
    Column("position_id", Integer, ForeignKey("positions.id")),
    Column("skill_id", Integer, ForeignKey("skills.id"))
)

# Association table for many-to-many relationship between Candidate and Skill
candidate_skill = Table(
    "candidate_skill",
    Base.metadata,
    Column("candidate_id", Integer, ForeignKey("candidates.id"), primary_key=True),
    Column("skill_id", Integer, ForeignKey("skills.id"), primary_key=True)
)

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    file_path = Column(String)
    content = Column(Text)
    category = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    offline_available = Column(Boolean, default=False)
    vector_id = Column(String, nullable=True)

class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=True)
    
    positions = relationship("Position", secondary=position_skill, back_populates="required_skills")
    candidates = relationship("Candidate", secondary=candidate_skill, back_populates="skills")

    def __repr__(self):
        return f"<Skill {self.name}>"

class Department(Base):
    """Department model for organizing job positions."""
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    
    positions = relationship("Position", back_populates="department", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Department {self.name}>"

class Position(Base):
    """Position model for job openings."""
    __tablename__ = "positions"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    requirements = Column(Text, nullable=True)
    responsibilities = Column(Text, nullable=True)
    location = Column(String(100), nullable=True)
    salary_range = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    created_date = Column(DateTime, default=datetime.now)
    updated_date = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    department = relationship("Department", back_populates="positions")
    required_skills = relationship("Skill", secondary=position_skill, back_populates="positions")
    candidates = relationship("Candidate", back_populates="position")
    applications = relationship("Application", back_populates="position", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Position {self.title}>"

class Candidate(Base):
    """Candidate model for job applicants."""
    __tablename__ = "candidates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=True)
    position_id = Column(Integer, ForeignKey("positions.id"), nullable=True)
    status = Column(String(20), default="New")  # New, Reviewing, Interview, Offer, Rejected, Hired
    resume_path = Column(String(255), nullable=True)
    resume_content = Column(Text, nullable=True)
    created_date = Column(DateTime, default=datetime.now)
    updated_date = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    skill_match_score = Column(Float, nullable=True)
    
    position = relationship("Position", back_populates="candidates")
    skills = relationship("Skill", secondary=candidate_skill, back_populates="candidates")
    applications = relationship("Application", back_populates="candidate", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="candidate", cascade="all, delete-orphan")
    interviews = relationship("Interview", back_populates="candidate", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Candidate {self.name}>"

class QuestionTemplate(Base):
    __tablename__ = "question_templates"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    difficulty = Column(String, default="Medium")  # Easy, Medium, Hard
    category = Column(String)  # Technical, Behavioral, Experience, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    
    question_sets = relationship("QuestionSet", back_populates="template")

class QuestionSet(Base):
    __tablename__ = "question_sets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    template_id = Column(Integer, ForeignKey("question_templates.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    template = relationship("QuestionTemplate", back_populates="question_sets")
    questions = relationship("Question", back_populates="question_set")
    interviews = relationship("Interview", back_populates="question_set")

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    difficulty = Column(String, default="Medium")  # Easy, Medium, Hard
    category = Column(String)  # Technical, Behavioral, Experience, etc.
    question_set_id = Column(Integer, ForeignKey("question_sets.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    question_set = relationship("QuestionSet", back_populates="questions")

class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    question_set_id = Column(Integer, ForeignKey("question_sets.id"), nullable=True)
    scheduled_date = Column(DateTime, nullable=True)
    status = Column(String, default="Scheduled")  # Scheduled, Completed, Cancelled
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    candidate = relationship("Candidate", back_populates="interviews")
    question_set = relationship("QuestionSet", back_populates="interviews")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    is_user = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    conversation_id = Column(String, index=True)
    saved = Column(Boolean, default=False)

class Application(Base):
    """Application model for job applications."""
    __tablename__ = "applications"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    position_id = Column(Integer, ForeignKey("positions.id"), nullable=False)
    status = Column(String(20), default="New")  # New, Reviewing, Interview, Offer, Rejected, Hired
    applied_date = Column(DateTime, default=datetime.now)
    status_updated_date = Column(DateTime, default=datetime.now)
    interview_date = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    
    candidate = relationship("Candidate", back_populates="applications")
    position = relationship("Position", back_populates="applications")
    
    def __repr__(self):
        return f"<Application {self.id}>"

class Note(Base):
    """Note model for candidate notes."""
    __tablename__ = "notes"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    content = Column(Text, nullable=False)
    note_type = Column(String(20), default="General")  # General, Interview, Reference, Offer
    created_date = Column(DateTime, default=datetime.now)
    updated_date = Column(DateTime, nullable=True)
    created_by = Column(String(100), nullable=True)
    
    candidate = relationship("Candidate", back_populates="notes")
    
    def __repr__(self):
        return f"<Note {self.id}>"

class User(Base):
    """User model for system users."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=True)
    hashed_password = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_date = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<User {self.username}>" 