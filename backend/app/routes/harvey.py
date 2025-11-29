from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, AIRecommendation
from app.routes.auth import get_current_user
from app.schemas import HarveyRecommendation, HarveySavings, HarveyAnomaly
from app.services.harvey import HarveyService
from datetime import datetime

router = APIRouter(prefix="/harvey", tags=["harvey"])

@router.get("/recommendations", response_model=list[HarveyRecommendation])
def get_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get Harvey AI recommendations."""
    harvey = HarveyService()
    recommendations = harvey.generate_recommendations(db, current_user.id)
    
    # Save recommendations to database
    for rec in recommendations:
        ai_rec = AIRecommendation(
            user_id=current_user.id,
            subscription_id=rec.get('subscription_id'),
            recommendation_text=rec['recommendation_text'],
            risk_score=rec['risk_score']
        )
        db.add(ai_rec)
    db.commit()
    
    return [
        HarveyRecommendation(
            subscription_id=rec.get('subscription_id'),
            recommendation_text=rec['recommendation_text'],
            risk_score=rec['risk_score'],
            created_at=datetime.now()
        )
        for rec in recommendations
    ]

@router.get("/savings", response_model=HarveySavings)
def get_savings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get savings calculations from Harvey."""
    harvey = HarveyService()
    savings = harvey.calculate_savings(db, current_user.id)
    return HarveySavings(**savings)

@router.get("/anomalies", response_model=list[HarveyAnomaly])
def get_anomalies(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detected anomalies."""
    harvey = HarveyService()
    anomalies = harvey.get_anomalies(db, current_user.id)
    return [HarveyAnomaly(**anom) for anom in anomalies]

