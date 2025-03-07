import logging
from sqlalchemy.orm import Session
from ..models.models import Department, Position, User
from ..services.auth_service import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add default departments
DEFAULT_DEPARTMENTS = [
    {"name": "Engineering", "description": "Software development and engineering"},
    {"name": "Product", "description": "Product management and design"},
    {"name": "Marketing", "description": "Marketing and communications"},
    {"name": "Sales", "description": "Sales and business development"},
    {"name": "Operations", "description": "Business operations and finance"},
    {"name": "Human Resources", "description": "Talent acquisition and employee management"},
    {"name": "Customer Success", "description": "Customer support and success"},
    {"name": "Legal", "description": "Legal and compliance"},
]

# Add some default positions
DEFAULT_POSITIONS = [
    {
        "title": "Software Engineer",
        "department_name": "Engineering",
        "description": "Design, develop, and maintain software applications",
        "requirements": "Bachelor's degree in Computer Science or related field. Proficiency in at least one programming language.",
        "salary_range": "$80,000 - $120,000",
        "location": "San Francisco, CA",
        "is_active": True
    },
    {
        "title": "Product Manager",
        "department_name": "Product",
        "description": "Lead product development and strategy",
        "requirements": "Bachelor's degree in Business or related field. 3+ years of product management experience.",
        "salary_range": "$90,000 - $140,000",
        "location": "New York, NY",
        "is_active": True
    },
    {
        "title": "HR Specialist",
        "department_name": "Human Resources",
        "description": "Support HR operations and employee management",
        "requirements": "Bachelor's degree in Human Resources or related field. 2+ years of HR experience.",
        "salary_range": "$60,000 - $90,000",
        "location": "Remote",
        "is_active": True
    },
]

# Create a default admin user
DEFAULT_ADMIN = {
    "username": "admin",
    "email": "admin@example.com",
    "password": "admin123",
    "full_name": "Admin User",
    "is_active": True,
    "is_superuser": True
}

def init_db(db: Session) -> None:
    """Initialize the database with default data."""
    # Add departments
    for dept_data in DEFAULT_DEPARTMENTS:
        existing_dept = db.query(Department).filter(Department.name == dept_data["name"]).first()
        if not existing_dept:
            dept = Department(**dept_data)
            db.add(dept)
            logger.info(f"Added department: {dept_data['name']}")
    db.commit()

    # Add positions
    for pos_data in DEFAULT_POSITIONS:
        department_name = pos_data.pop("department_name")
        department = db.query(Department).filter(Department.name == department_name).first()
        if not department:
            logger.warning(f"Department {department_name} not found, skipping position")
            continue

        existing_position = db.query(Position).filter(
            Position.title == pos_data["title"],
            Position.department_id == department.id
        ).first()

        if not existing_position:
            position = Position(
                title=pos_data["title"],
                department_id=department.id,
                description=pos_data["description"],
                requirements=pos_data["requirements"],
                salary_range=pos_data["salary_range"],
                is_active=pos_data["is_active"]
            )
            db.add(position)
            logger.info(f"Added position: {pos_data['title']}")
    db.commit()

    # Add admin user
    admin_data = DEFAULT_ADMIN.copy()
    password = admin_data.pop("password")
    existing_admin = db.query(User).filter(User.username == admin_data["username"]).first()
    
    if not existing_admin:
        hashed_password = get_password_hash(password)
        admin = User(**admin_data, hashed_password=hashed_password)
        db.add(admin)
        logger.info(f"Added admin user: {admin_data['username']}")
        db.commit()

if __name__ == "__main__":
    # This allows running this module directly
    from ..db.database import SessionLocal
    
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close() 