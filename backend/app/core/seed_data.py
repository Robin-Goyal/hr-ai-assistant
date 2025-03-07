from sqlalchemy.orm import Session
import os
import sys
import logging

from ..db.database import get_db
from ..models.models import Department, Position

logger = logging.getLogger("uvicorn")

def should_seed_data(db: Session) -> bool:
    """
    Check if data seeding is needed by checking if tables are empty.
    """
    # Check if we're in development environment
    env = os.getenv("ENVIRONMENT", "development")
    if env != "development":
        logger.info("Not in development environment, skipping data seeding")
        return False
    
    # Check if tables are empty
    department_count = db.query(Department).count()
    position_count = db.query(Position).count()
    
    if department_count > 0 and position_count > 0:
        logger.info(f"Database already contains {department_count} departments and {position_count} positions. Skipping seeding.")
        return False
    
    return True

def seed_departments(db: Session) -> int:
    """Add sample departments to the database."""
    # Sample departments
    departments = [
        {"name": "Engineering", "description": "Software development and engineering teams"},
        {"name": "Product", "description": "Product management and design"},
        {"name": "Sales", "description": "Sales and business development"},
        {"name": "Marketing", "description": "Marketing, brand, and communications"},
        {"name": "Finance", "description": "Finance, accounting, and legal"},
        {"name": "Human Resources", "description": "HR, recruiting, and employee experience"},
        {"name": "Operations", "description": "Operations, IT, and facilities"},
        {"name": "Customer Success", "description": "Customer support and success"},
        {"name": "Research", "description": "Research and development"},
        {"name": "Data Science", "description": "Data analytics and machine learning"}
    ]
    
    # Add departments to the database
    departments_added = 0
    for dept_data in departments:
        # Check if department already exists
        existing = db.query(Department).filter(Department.name == dept_data["name"]).first()
        if not existing:
            department = Department(**dept_data)
            db.add(department)
            departments_added += 1
    
    # Commit changes
    db.commit()
    
    return departments_added

def seed_positions(db: Session) -> int:
    """Add sample positions to the database."""
    # Get department IDs
    departments = {dept.name: dept.id for dept in db.query(Department).all()}
    
    if not departments:
        logger.warning("No departments found. Skipping position seeding.")
        return 0
    
    # Sample positions
    positions = [
        {
            "title": "Senior Software Engineer",
            "description": "Lead software development efforts and mentor junior engineers",
            "requirements": "5+ years of experience in software development, proficiency in Python and JavaScript",
            "responsibilities": "Design and implement software solutions, code reviews, mentoring junior engineers",
            "location": "San Francisco, CA",
            "salary_range": "$120,000 - $160,000",
            "is_active": True,
            "department_id": departments.get("Engineering")
        },
        {
            "title": "Product Manager",
            "description": "Oversee product development and strategy",
            "requirements": "3+ years of product management experience, strong analytical skills",
            "responsibilities": "Define product roadmap, collaborate with engineering and design teams, conduct market research",
            "location": "New York, NY",
            "salary_range": "$110,000 - $150,000",
            "is_active": True,
            "department_id": departments.get("Product")
        },
        {
            "title": "Sales Representative",
            "description": "Drive sales and customer acquisition",
            "requirements": "Proven sales experience, excellent communication skills",
            "responsibilities": "Prospect new clients, conduct product demonstrations, achieve sales targets",
            "location": "Chicago, IL",
            "salary_range": "$60,000 - $90,000 + Commission",
            "is_active": True,
            "department_id": departments.get("Sales")
        },
        {
            "title": "Marketing Specialist",
            "description": "Execute marketing campaigns and content creation",
            "requirements": "2+ years of marketing experience, proficiency in digital marketing tools",
            "responsibilities": "Create marketing content, manage social media, analyze campaign performance",
            "location": "Remote",
            "salary_range": "$70,000 - $95,000",
            "is_active": True,
            "department_id": departments.get("Marketing")
        },
        {
            "title": "Financial Analyst",
            "description": "Analyze financial data and support business decisions",
            "requirements": "Finance or accounting degree, experience with financial modeling",
            "responsibilities": "Financial forecasting, budget planning, investment analysis",
            "location": "Boston, MA",
            "salary_range": "$85,000 - $115,000",
            "is_active": True,
            "department_id": departments.get("Finance")
        },
        {
            "title": "HR Coordinator",
            "description": "Support HR operations and employee experience",
            "requirements": "HR experience, knowledge of employment laws",
            "responsibilities": "Onboarding new employees, maintaining employee records, supporting recruitment",
            "location": "Austin, TX",
            "salary_range": "$55,000 - $75,000",
            "is_active": True,
            "department_id": departments.get("Human Resources")
        },
        {
            "title": "Operations Manager",
            "description": "Oversee daily operations and process improvements",
            "requirements": "5+ years of operations experience, project management skills",
            "responsibilities": "Optimize operational processes, manage resources, implement best practices",
            "location": "Seattle, WA",
            "salary_range": "$90,000 - $130,000",
            "is_active": True,
            "department_id": departments.get("Operations")
        },
        {
            "title": "Customer Support Specialist",
            "description": "Provide exceptional customer service and support",
            "requirements": "Experience in customer service, problem-solving skills",
            "responsibilities": "Respond to customer inquiries, resolve issues, document customer feedback",
            "location": "Remote",
            "salary_range": "$50,000 - $70,000",
            "is_active": True,
            "department_id": departments.get("Customer Success")
        },
        {
            "title": "Research Scientist",
            "description": "Conduct research and develop new technologies",
            "requirements": "PhD in relevant field, experience in research methodologies",
            "responsibilities": "Design and conduct experiments, analyze results, publish findings",
            "location": "San Diego, CA",
            "salary_range": "$130,000 - $180,000",
            "is_active": True,
            "department_id": departments.get("Research")
        },
        {
            "title": "Data Scientist",
            "description": "Extract insights from data and develop machine learning models",
            "requirements": "Strong statistical background, experience with Python and machine learning libraries",
            "responsibilities": "Develop machine learning models, analyze complex datasets, create data visualizations",
            "location": "San Francisco, CA",
            "salary_range": "$120,000 - $170,000",
            "is_active": True,
            "department_id": departments.get("Data Science")
        }
    ]
    
    # Add positions to the database
    positions_added = 0
    for pos_data in positions:
        # Skip if department_id is not found
        if not pos_data.get("department_id"):
            logger.warning(f"Skipping position '{pos_data['title']}' due to missing department ID")
            continue
            
        # Check if position already exists
        existing = db.query(Position).filter(
            Position.title == pos_data["title"],
            Position.department_id == pos_data["department_id"]
        ).first()
        
        if not existing:
            position = Position(**pos_data)
            db.add(position)
            positions_added += 1
    
    # Commit changes
    db.commit()
    
    return positions_added

def seed_data():
    """Seed the database with initial data if needed."""
    # Get DB session
    db = next(get_db())
    
    if not should_seed_data(db):
        return
    
    logger.info("Seeding database with initial data...")
    
    # Seed departments first
    dept_count = seed_departments(db)
    logger.info(f"Added {dept_count} departments to the database")
    
    # Then seed positions
    if dept_count > 0:
        pos_count = seed_positions(db)
        logger.info(f"Added {pos_count} positions to the database")
    
    logger.info("Database seeding completed") 