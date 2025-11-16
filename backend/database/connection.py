from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from decouple import config
from backend.database.models import Base

DATABASE_URL = config("DATABASE_URL", default="sqlite:///./genai_chatbot.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Database dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")
