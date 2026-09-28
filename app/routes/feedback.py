from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.feedback import Feedback
from app.schemas.feedback import FeedbackCreate, FeedbackResponse
from app.services.sentiment_service import sentiment_service
from app.dependencies import get_required_customer

router = APIRouter(prefix="/feedback", tags=["Customer Feedback"])

@router.post("", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def submit_feedback(
    payload: FeedbackCreate,
    current_customer: User = Depends(get_required_customer),
    db: Session = Depends(get_db)
):
    text = payload.feedback_text.strip()
    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Feedback text cannot be empty or blank."
        )
    
    if len(text) > 2000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Feedback text exceeds maximum length of 2000 characters."
        )

    # Automatic sentiment prediction using loaded ML model
    predicted_sentiment = sentiment_service.predict(text)

    feedback_record = Feedback(
        customer_id=current_customer.id,
        feedback_text=text,
        sentiment=predicted_sentiment
    )

    db.add(feedback_record)
    db.commit()
    db.refresh(feedback_record)

    return FeedbackResponse(
        id=feedback_record.id,
        customer_id=feedback_record.customer_id,
        customer_name=current_customer.name,
        customer_email=current_customer.email,
        feedback_text=feedback_record.feedback_text,
        sentiment=feedback_record.sentiment,
        created_at=feedback_record.created_at
    )

@router.get("/my", response_model=List[FeedbackResponse])
def get_my_feedback(
    current_customer: User = Depends(get_required_customer),
    db: Session = Depends(get_db)
):
    records = db.query(Feedback)\
        .filter(Feedback.customer_id == current_customer.id)\
        .order_by(Feedback.created_at.desc())\
        .all()
    
    return [
        FeedbackResponse(
            id=item.id,
            customer_id=item.customer_id,
            customer_name=current_customer.name,
            customer_email=current_customer.email,
            feedback_text=item.feedback_text,
            sentiment=item.sentiment,
            created_at=item.created_at
        )
        for item in records
    ]
