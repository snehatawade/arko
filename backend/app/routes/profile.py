from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Transaction
from app.routes.auth import get_current_user
from app.schemas import ProfileResponse, ProfileUpdate

router = APIRouter(prefix="/profile", tags=["profile"])

@router.get("", response_model=ProfileResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile."""
    return ProfileResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        phone=current_user.phone,
        created_at=current_user.created_at
    )

@router.patch("", response_model=ProfileResponse)
def update_profile(
    profile_update: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile."""
    if profile_update.name:
        current_user.name = profile_update.name
    if profile_update.phone:
        current_user.phone = profile_update.phone
    # notification_preferences can be stored in a separate table or JSON field
    # For MVP, we'll skip this
    
    db.commit()
    db.refresh(current_user)
    
    return ProfileResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        phone=current_user.phone,
        created_at=current_user.created_at
    )

@router.delete("")
def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete user account."""
    # In production, you might want to soft delete
    db.delete(current_user)
    db.commit()
    return {"message": "Account deleted successfully"}

@router.get("/csv-history")
def get_csv_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get history of uploaded CSV files (grouped by bank_account)."""
    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).all()
    
    # Group by bank_account
    bank_accounts = {}
    for txn in transactions:
        if txn.bank_account not in bank_accounts:
            bank_accounts[txn.bank_account] = {
                'bank_account': txn.bank_account,
                'first_upload': txn.date,
                'last_upload': txn.date,
                'transaction_count': 0
            }
        bank_accounts[txn.bank_account]['last_upload'] = max(
            bank_accounts[txn.bank_account]['last_upload'], txn.date
        )
        bank_accounts[txn.bank_account]['first_upload'] = min(
            bank_accounts[txn.bank_account]['first_upload'], txn.date
        )
        bank_accounts[txn.bank_account]['transaction_count'] += 1
    
    return list(bank_accounts.values())

