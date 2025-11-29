from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

# Auth Schemas
class UserSignup(BaseModel):
    name: str
    email: EmailStr
    phone: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Transaction Schemas
class TransactionCreate(BaseModel):
    date: datetime
    amount: float
    description: str
    bank_account: str
    raw_text: Optional[str] = None

class TransactionResponse(BaseModel):
    id: int
    date: datetime
    amount: float
    description: str
    bank_account: str
    
    class Config:
        from_attributes = True

# Subscription Schemas
class SubscriptionResponse(BaseModel):
    id: int
    name: str
    amount: float
    frequency: str
    first_seen: datetime
    last_seen: datetime
    next_renewal: datetime
    bank_account: str
    status: str
    
    class Config:
        from_attributes = True

class SubscriptionDetailResponse(SubscriptionResponse):
    cancellation_probability: Optional[float] = None
    harvey_insights: Optional[str] = None
    transactions: List[TransactionResponse] = []

# Harvey Schemas
class HarveyRecommendation(BaseModel):
    subscription_id: Optional[int]
    recommendation_text: str
    risk_score: float
    created_at: datetime

class HarveySavings(BaseModel):
    total_monthly_cost: float
    avoidable_spend: float
    potential_savings: float

class HarveyAnomaly(BaseModel):
    subscription_id: int
    anomaly_type: str
    description: str
    risk_score: float

# Profile Schemas
class ProfileResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    notification_preferences: Optional[dict] = None

