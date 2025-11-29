import pandas as pd
import re
from typing import List, Dict
from datetime import datetime

def clean_merchant_name(description: str) -> str:
    """Clean and normalize merchant names from transaction descriptions."""
    # Remove common prefixes/suffixes
    description = description.lower()
    
    # Remove common patterns
    patterns_to_remove = [
        r'^payment\s+',
        r'^transfer\s+',
        r'^debit\s+',
        r'^credit\s+',
        r'\s+payment$',
        r'\s+subscription$',
        r'\d{4}.*$',  # Remove trailing numbers (card numbers, etc.)
    ]
    
    for pattern in patterns_to_remove:
        description = re.sub(pattern, '', description, flags=re.IGNORECASE)
    
    # Remove special characters but keep spaces
    description = re.sub(r'[^\w\s]', '', description)
    
    # Remove extra whitespace
    description = ' '.join(description.split())
    
    return description.strip()

def normalize_transactions(transactions: List[Dict]) -> pd.DataFrame:
    """Normalize transaction data into a pandas DataFrame."""
    df = pd.DataFrame(transactions)
    
    # Ensure date is datetime
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    
    # Clean merchant names
    if 'description' in df.columns:
        df['merchant'] = df['description'].apply(clean_merchant_name)
    
    # Ensure amount is numeric
    if 'amount' in df.columns:
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    
    # Sort by date
    df = df.sort_values('date')
    
    return df

def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """Extract features for ML model."""
    features_df = df.copy()
    
    # Time-based features
    features_df['day_of_month'] = features_df['date'].dt.day
    features_df['month'] = features_df['date'].dt.month
    features_df['year'] = features_df['date'].dt.year
    
    # Amount features
    features_df['amount_abs'] = features_df['amount'].abs()
    
    # Group by merchant to calculate statistics
    merchant_stats = features_df.groupby('merchant').agg({
        'amount_abs': ['mean', 'std', 'count'],
        'date': ['min', 'max']
    }).reset_index()
    
    merchant_stats.columns = ['merchant', 'avg_amount', 'std_amount', 'transaction_count', 'first_seen', 'last_seen']
    
    # Calculate days between transactions
    merchant_stats['days_between'] = (
        merchant_stats['last_seen'] - merchant_stats['first_seen']
    ).dt.days / (merchant_stats['transaction_count'] - 1).replace(0, 1)
    
    return merchant_stats

