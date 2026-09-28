from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    feedback_text = Column(Text, nullable=False)
    sentiment = Column(String(50), nullable=False) # 'positive', 'neutral', 'negative'
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


    customer = relationship("User", back_populates="feedbacks")
