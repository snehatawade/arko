import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from app.ml.preprocess import normalize_transactions, extract_features, clean_merchant_name

def detect_recurring_subscriptions(transactions: List[Dict], user_id: int) -> List[Dict]:
    """
    Detect recurring subscriptions from transaction data.
    Returns list of subscription dictionaries.
    """
    if not transactions:
        return []
    
    # Normalize transactions
    df = normalize_transactions(transactions)
    
    if df.empty:
        return []
    
    # Group by merchant
    merchant_groups = df.groupby('merchant')
    
    subscriptions = []
    
    for merchant, group in merchant_groups:
        if len(group) < 2:  # Need at least 2 transactions to be recurring
            continue
        
        # Calculate statistics
        amounts = group['amount'].abs().values
        dates = group['date'].values
        
        # Check if amounts are similar (within 10% variance)
        amount_std = np.std(amounts)
        amount_mean = np.mean(amounts)
        if amount_std / amount_mean > 0.1:
            continue  # Too much variance in amounts
        
        # Calculate frequency using pandas Timedelta (handles numpy timedelta64)
        sorted_dates = pd.Series(dates).sort_values()
        date_diffs = sorted_dates.diff().dropna()
        positive_diffs = date_diffs[date_diffs.dt.days > 0]
        if positive_diffs.empty:
            continue
        avg_days = positive_diffs.dt.days.mean()
        
        if avg_days is None or avg_days <= 0:
            continue
        
        # Determine frequency
        if 25 <= avg_days <= 35:
            frequency = "monthly"
        elif 360 <= avg_days <= 375:
            frequency = "yearly"
        else:
            frequency = "other"
        
        # Get latest transaction
        latest = group.iloc[-1]
        first = group.iloc[0]
        
        # Calculate next renewal
        if frequency == "monthly":
            next_renewal = latest['date'] + timedelta(days=30)
        elif frequency == "yearly":
            next_renewal = latest['date'] + timedelta(days=365)
        else:
            next_renewal = latest['date'] + timedelta(days=int(avg_days))
        
        subscription = {
            'user_id': user_id,
            'name': merchant.title(),
            'amount': float(amount_mean),
            'frequency': frequency,
            'first_seen': first['date'],
            'last_seen': latest['date'],
            'next_renewal': next_renewal,
            'bank_account': latest.get('bank_account', 'Unknown'),
            'status': 'active'
        }
        
        subscriptions.append(subscription)
    
    return subscriptions

def detect_price_anomalies(subscriptions: List[Dict], transactions: List[Dict]) -> List[Dict]:
    """Detect price increases in subscriptions."""
    anomalies = []
    
    df = normalize_transactions(transactions)
    
    for sub in subscriptions:
        merchant = clean_merchant_name(sub['name'])
        merchant_transactions = df[df['merchant'] == merchant]
        
        if len(merchant_transactions) < 2:
            continue
        
        amounts = merchant_transactions['amount'].abs().values
        dates = merchant_transactions['date'].values
        
        # Check for price increase (more than 10%)
        if len(amounts) >= 2:
            old_avg = np.mean(amounts[:-1])
            new_amount = amounts[-1]
            
            if new_amount > old_avg * 1.1:  # 10% increase
                anomalies.append({
                    'subscription_id': sub.get('id'),
                    'anomaly_type': 'price_increase',
                    'description': f"Price increased from ₹{old_avg:.2f} to ₹{new_amount:.2f}",
                    'risk_score': 0.7
                })
    
    return anomalies

def calculate_usage_frequency(transactions: List[Dict], subscription: Dict) -> float:
    """Calculate usage frequency score (0-1, higher = more active)."""
    df = normalize_transactions(transactions)
    merchant = clean_merchant_name(subscription['name'])
    merchant_transactions = df[df['merchant'] == merchant]
    
    if len(merchant_transactions) < 2:
        return 0.5  # Default moderate usage
    
    # Calculate time span
    time_span = (merchant_transactions['date'].max() - merchant_transactions['date'].min()).days
    if time_span == 0:
        return 0.5
    
    # Transactions per month
    transactions_per_month = len(merchant_transactions) / (time_span / 30.0)
    
    # Normalize to 0-1 scale (assuming 1-4 transactions/month is normal)
    usage_score = min(1.0, transactions_per_month / 4.0)
    
    return usage_score

def predict_cancellation_probability(subscription: Dict, usage_score: float, days_since_last: int) -> float:
    """Predict probability of cancellation (0-1)."""
    # Factors that increase cancellation probability:
    # - Low usage score
    # - Long time since last transaction
    # - High price relative to usage
    
    prob = 0.0
    
    # Low usage increases probability
    if usage_score < 0.3:
        prob += 0.4
    elif usage_score < 0.5:
        prob += 0.2
    
    # Long time since last transaction
    if days_since_last > 60:
        prob += 0.3
    elif days_since_last > 30:
        prob += 0.15
    
    # High price with low usage
    if subscription['amount'] > 10 and usage_score < 0.4:
        prob += 0.2
    
    return min(1.0, prob)

