from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.feedback import Feedback
from app.schemas.feedback import FeedbackResponse, StatsResponse
from app.dependencies import get_required_support

router = APIRouter(prefix="/support", tags=["Support Team Dashboard"])

def _build_feedback_response(fb: Feedback) -> FeedbackResponse:
    return FeedbackResponse(
        id=fb.id,
        customer_id=fb.customer_id,
        customer_name=fb.customer.name if fb.customer else "Unknown Customer",
        customer_email=fb.customer.email if fb.customer else "N/A",
        feedback_text=fb.feedback_text,
        sentiment=fb.sentiment,
        created_at=fb.created_at
    )

@router.get("/feedback", response_model=List[FeedbackResponse])
def get_all_feedback(
    sentiment: Optional[str] = Query(None, description="Filter by sentiment: positive, neutral, negative"),
    search: Optional[str] = Query(None, description="Search term for customer name or feedback text"),
    sort: Optional[str] = Query("desc", description="Sort direction: desc (newest first) or asc (oldest first)"),
    support_user: User = Depends(get_required_support),
    db: Session = Depends(get_db)
):
    query = db.query(Feedback).join(User, Feedback.customer_id == User.id)

    if sentiment:
        query = query.filter(Feedback.sentiment == sentiment.lower())

    if search:
        search_pattern = f"%{search.strip()}%"
        query = query.filter(
            (Feedback.feedback_text.ilike(search_pattern)) | 
            (User.name.ilike(search_pattern)) |
            (User.email.ilike(search_pattern))
        )

    if sort == "asc":
        query = query.order_by(Feedback.created_at.asc())
    else:
        query = query.order_by(Feedback.created_at.desc())

    records = query.all()
    return [_build_feedback_response(fb) for fb in records]

@router.get("/feedback/positive", response_model=List[FeedbackResponse])
def get_positive_feedback(
    support_user: User = Depends(get_required_support),
    db: Session = Depends(get_db)
):
    records = db.query(Feedback).join(User, Feedback.customer_id == User.id)\
        .filter(Feedback.sentiment == "positive")\
        .order_by(Feedback.created_at.desc())\
        .all()
    return [_build_feedback_response(fb) for fb in records]

@router.get("/feedback/neutral", response_model=List[FeedbackResponse])
def get_neutral_feedback(
    support_user: User = Depends(get_required_support),
    db: Session = Depends(get_db)
):
    records = db.query(Feedback).join(User, Feedback.customer_id == User.id)\
        .filter(Feedback.sentiment == "neutral")\
        .order_by(Feedback.created_at.desc())\
        .all()
    return [_build_feedback_response(fb) for fb in records]

@router.get("/feedback/negative", response_model=List[FeedbackResponse])
def get_negative_feedback(
    support_user: User = Depends(get_required_support),
    db: Session = Depends(get_db)
):
    records = db.query(Feedback).join(User, Feedback.customer_id == User.id)\
        .filter(Feedback.sentiment == "negative")\
        .order_by(Feedback.created_at.desc())\
        .all()
    return [_build_feedback_response(fb) for fb in records]

@router.get("/stats", response_model=StatsResponse)
def get_sentiment_stats(
    support_user: User = Depends(get_required_support),
    db: Session = Depends(get_db)
):
    total = db.query(Feedback).count()
    positive = db.query(Feedback).filter(Feedback.sentiment == "positive").count()
    neutral = db.query(Feedback).filter(Feedback.sentiment == "neutral").count()
    negative = db.query(Feedback).filter(Feedback.sentiment == "negative").count()

    return StatsResponse(
        total=total,
        positive=positive,
        neutral=neutral,
        negative=negative
    )
