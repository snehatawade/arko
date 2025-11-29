from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Transaction, Subscription
from app.routes.auth import get_current_user
from app.services.csv_parser import parse_csv, parse_excel
from app.ml.detect import detect_recurring_subscriptions
from app.services.notifications import notification_service
from datetime import datetime

router = APIRouter(prefix="/upload", tags=["upload"])

@router.post("/csv")
def upload_csv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload and process CSV or Excel bank statement."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    file_ext = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    
    if file_ext not in ['csv', 'xlsx', 'xls']:
        raise HTTPException(status_code=400, detail=f"File must be a CSV or Excel file (.csv, .xlsx, .xls). Got: {file_ext}")
    
    print(f"Processing file: {file.filename}, extension: {file_ext}, content_type: {file.content_type}")
    
    # Read file content
    try:
        if file_ext == 'csv':
            content = file.file.read().decode('utf-8')
            print(f"CSV content length: {len(content)}")
            transactions_data = parse_csv(content)
        else:
            # Handle Excel files
            import pandas as pd
            from io import BytesIO
            file_content = file.file.read()
            print(f"Excel file size: {len(file_content)} bytes")
            df = pd.read_excel(BytesIO(file_content))
            print(f"Excel columns: {df.columns.tolist()}")
            transactions_data = parse_excel(df)
        print(f"Parsed {len(transactions_data)} transactions")
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = str(e)
        print(f"Upload error: {error_detail}")
        traceback.print_exc()
        # Provide more helpful error message
        if "columns" in error_detail.lower():
            raise HTTPException(status_code=400, detail=error_detail)
        else:
            raise HTTPException(status_code=400, detail=f"Error parsing file: {error_detail}. Please check that your file has columns: date, amount, and description (or raw_descr)")
    
    # Save transactions to database
    new_transactions = []
    for txn_data in transactions_data:
        transaction = Transaction(
            user_id=current_user.id,
            date=txn_data['date'],
            amount=txn_data['amount'],
            description=txn_data['description'],
            bank_account=txn_data['bank_account'],
            raw_text=txn_data.get('raw_text')
        )
        db.add(transaction)
        new_transactions.append(transaction)
    
    db.commit()
    
    # Detect recurring subscriptions
    subscriptions = detect_recurring_subscriptions(transactions_data, current_user.id)
    
    # Check for new subscriptions and save them
    new_subscriptions = []
    for sub_data in subscriptions:
        # Check if subscription already exists
        existing = db.query(Subscription).filter(
            Subscription.user_id == current_user.id,
            Subscription.name == sub_data['name'],
            Subscription.status == "active"
        ).first()
        
        if not existing:
            subscription = Subscription(**sub_data)
            db.add(subscription)
            db.commit()
            db.refresh(subscription)
            new_subscriptions.append(subscription)
            
            # Send notification for new subscription
            notification_service.send_new_subscription_alert(current_user, subscription)
        else:
            # Update existing subscription
            existing.last_seen = sub_data['last_seen']
            existing.next_renewal = sub_data['next_renewal']
            existing.amount = sub_data['amount']
            db.commit()
    
    return {
        "message": "CSV processed successfully",
        "transactions_added": len(new_transactions),
        "subscriptions_detected": len(subscriptions),
        "new_subscriptions": len(new_subscriptions)
    }

