from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from app.database import Base

class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    transactions = relationship("Transaction", back_populates="user")
    subscriptions = relationship("Subscription", back_populates="user")
    ai_recommendations = relationship("AIRecommendation", back_populates="user")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String, nullable=False)
    bank_account = Column(String, nullable=False)
    raw_text = Column(Text)
    
    user = relationship("User", back_populates="transactions")

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    frequency = Column(String, nullable=False)  # monthly, yearly, other
    first_seen = Column(DateTime, nullable=False)
    last_seen = Column(DateTime, nullable=False)
    next_renewal = Column(DateTime, nullable=False)
    bank_account = Column(String, nullable=False)
    status = Column(SQLEnum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE)
    
    user = relationship("User", back_populates="subscriptions")
    ai_recommendations = relationship("AIRecommendation", back_populates="subscription")

class AIRecommendation(Base):
    __tablename__ = "ai_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=True)
    recommendation_text = Column(Text, nullable=False)
    risk_score = Column(Float, default=0.0)
    created_at = Column(DateTime, server_default=func.now())
    
    user = relationship("User", back_populates="ai_recommendations")
    subscription = relationship("Subscription", back_populates="ai_recommendations")

