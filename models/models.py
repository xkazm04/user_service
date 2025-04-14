from sqlalchemy.dialects.postgresql import UUID
from database import Base
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True) 
    email = Column(String, unique=True, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    credits = Column(Integer, default=0, nullable=False)  
    plan = Column(String, nullable=False)  
    created_at = Column(DateTime, default=datetime.utcnow)
