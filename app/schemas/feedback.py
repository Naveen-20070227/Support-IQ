from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class FeedbackCreate(BaseModel):
    feedback_text: str = Field(..., min_length=1, max_length=2000, description="Customer review text")


class FeedbackResponse(BaseModel):
    id: int
    customer_id: int
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    feedback_text: str
    sentiment: str
    created_at: datetime

    class Config:
        from_attributes = True

class StatsResponse(BaseModel):
    total: int
    positive: int
    neutral: int
    negative: int
