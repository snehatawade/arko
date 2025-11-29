from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Subscription, Transaction
from app.routes.auth import get_current_user
from app.schemas import SubscriptionResponse, SubscriptionDetailResponse, TransactionResponse
from app.services.harvey import HarveyService
from app.ml.detect import calculate_usage_frequency, predict_cancellation_probability
from app.ml.preprocess import normalize_transactions
from datetime import datetime

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])

@router.get("", response_model=list[SubscriptionResponse])
def get_subscriptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all subscriptions for current user."""
    subscriptions = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.status == "active"
    ).all()
    return subscriptions

@router.get("/{subscription_id}", response_model=SubscriptionDetailResponse)
def get_subscription_detail(
    subscription_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed information about a subscription."""
    subscription = db.query(Subscription).filter(
        Subscription.id == subscription_id,
        Subscription.user_id == current_user.id
    ).first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    # Get related transactions
    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).all()
    
    # Filter transactions for this subscription (by merchant name)
    from app.ml.preprocess import clean_merchant_name
    merchant_name = clean_merchant_name(subscription.name)
    
    related_transactions = []
    for txn in transactions:
        if clean_merchant_name(txn.description) == merchant_name:
            related_transactions.append(TransactionResponse(
                id=txn.id,
                date=txn.date,
                amount=txn.amount,
                description=txn.description,
                bank_account=txn.bank_account
            ))
    
    # Calculate cancellation probability
    transactions_data = [
        {
            'date': t.date,
            'amount': t.amount,
            'description': t.description,
            'bank_account': t.bank_account
        }
        for t in transactions
    ]
    
    sub_dict = {
        'id': subscription.id,
        'name': subscription.name,
        'amount': subscription.amount,
        'frequency': subscription.frequency
    }
    
    usage_score = calculate_usage_frequency(transactions_data, sub_dict)
    days_since_last = (datetime.now() - subscription.last_seen).days
    cancel_prob = predict_cancellation_probability(sub_dict, usage_score, days_since_last)
    
    # Get Harvey insights
    harvey_service = HarveyService()
    recommendations = harvey_service.generate_recommendations(db, current_user.id)
    harvey_insights = "\n".join([
        rec['recommendation_text'] 
        for rec in recommendations 
        if rec.get('subscription_id') == subscription_id
    ])
    
    return SubscriptionDetailResponse(
        id=subscription.id,
        name=subscription.name,
        amount=subscription.amount,
        frequency=subscription.frequency,
        first_seen=subscription.first_seen,
        last_seen=subscription.last_seen,
        next_renewal=subscription.next_renewal,
        bank_account=subscription.bank_account,
        status=subscription.status.value,
        cancellation_probability=cancel_prob,
        harvey_insights=harvey_insights if harvey_insights else None,
        transactions=related_transactions
    )

@router.patch("/{subscription_id}/cancel")
def cancel_subscription(
    subscription_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a subscription as cancelled."""
    subscription = db.query(Subscription).filter(
        Subscription.id == subscription_id,
        Subscription.user_id == current_user.id
    ).first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    subscription.status = "cancelled"
    db.commit()
    
    return {"message": "Subscription cancelled successfully"}

