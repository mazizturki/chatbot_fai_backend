from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .base import Base

DATABASE_URL = "postgresql://postgres:14774368@localhost:5432/fsi"  

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()