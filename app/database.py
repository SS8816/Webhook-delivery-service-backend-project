from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from sqlalchemy.ext.declarative import declarative_base

from app.models import Base

# Replace with your actual DB URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:shub1234@localhost/webhooks")

# Engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
# Create tables (if needed, though Alembic handles this)
def init_db():
    Base.metadata.create_all(bind=engine)
