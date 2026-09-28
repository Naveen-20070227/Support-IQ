from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="customer") # 'customer' or 'support'
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


    feedbacks = relationship("Feedback", back_populates="customer", cascade="all, delete-orphan")
