from typing import List, Dict
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models import Subscription, Transaction, AIRecommendation
from app.ml.detect import detect_price_anomalies, calculate_usage_frequency, predict_cancellation_probability
from app.ml.preprocess import normalize_transactions

class HarveyService:
    """AI Agent Harvey - Provides insights and recommendations."""
    
    @staticmethod
    def generate_recommendations(db: Session, user_id: int) -> List[Dict]:
        """Generate AI recommendations for user."""
        subscriptions = db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.status == "active"
        ).all()
        
        transactions = db.query(Transaction).filter(
            Transaction.user_id == user_id
        ).all()
        
        if not subscriptions:
            return []
        
        # Convert to dicts for ML functions
        transactions_data = [
            {
                'date': t.date,
                'amount': t.amount,
                'description': t.description,
                'bank_account': t.bank_account
            }
            for t in transactions
        ]
        
        recommendations = []
        
        for sub in subscriptions:
            sub_dict = {
                'id': sub.id,
                'name': sub.name,
                'amount': sub.amount,
                'frequency': sub.frequency
            }
            
            # Calculate usage frequency
            usage_score = calculate_usage_frequency(transactions_data, sub_dict)
            
            # Calculate days since last seen
            days_since_last = (datetime.now() - sub.last_seen).days
            
            # Predict cancellation probability
            cancel_prob = predict_cancellation_probability(sub_dict, usage_score, days_since_last)
            
            # Generate recommendation text
            recommendation_text = ""
            risk_score = 0.0
            
            if cancel_prob > 0.7:
                recommendation_text = f"⚠️ High cancellation risk for {sub.name}. Consider reviewing usage."
                risk_score = cancel_prob
            elif usage_score < 0.3:
                recommendation_text = f"💡 Low usage detected for {sub.name}. You may want to cancel to save ₹{sub.amount:.2f}/{sub.frequency}."
                risk_score = 0.6
            elif sub.amount > 20 and usage_score < 0.5:
                recommendation_text = f"💰 {sub.name} costs ₹{sub.amount:.2f} but shows low usage. Potential savings: ₹{sub.amount:.2f}/{sub.frequency}."
                risk_score = 0.5
            
            if recommendation_text:
                recommendations.append({
                    'subscription_id': sub.id,
                    'recommendation_text': recommendation_text,
                    'risk_score': risk_score
                })
        
        # Check for price anomalies
        subscriptions_data = [
            {
                'id': sub.id,
                'name': sub.name,
                'amount': sub.amount,
                'frequency': sub.frequency
            }
            for sub in subscriptions
        ]
        
        anomalies = detect_price_anomalies(subscriptions_data, transactions_data)
        for anomaly in anomalies:
            recommendations.append({
                'subscription_id': anomaly['subscription_id'],
                'recommendation_text': f"📈 {anomaly['description']}",
                'risk_score': anomaly['risk_score']
            })
        
        return recommendations
    
    @staticmethod
    def calculate_savings(db: Session, user_id: int) -> Dict:
        """Calculate potential savings."""
        subscriptions = db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.status == "active"
        ).all()
        
        total_monthly = 0.0
        avoidable_spend = 0.0
        
        transactions = db.query(Transaction).filter(
            Transaction.user_id == user_id
        ).all()
        
        transactions_data = [
            {
                'date': t.date,
                'amount': t.amount,
                'description': t.description,
                'bank_account': t.bank_account
            }
            for t in transactions
        ]
        
        for sub in subscriptions:
            # Convert to monthly cost
            if sub.frequency == "monthly":
                monthly_cost = sub.amount
            elif sub.frequency == "yearly":
                monthly_cost = sub.amount / 12
            else:
                monthly_cost = sub.amount  # Assume monthly
            
            total_monthly += monthly_cost
            
            # Check if low usage (potential waste)
            sub_dict = {
                'id': sub.id,
                'name': sub.name,
                'amount': sub.amount,
                'frequency': sub.frequency
            }
            usage_score = calculate_usage_frequency(transactions_data, sub_dict)
            
            if usage_score < 0.3:
                avoidable_spend += monthly_cost
        
        return {
            'total_monthly_cost': total_monthly,
            'avoidable_spend': avoidable_spend,
            'potential_savings': avoidable_spend
        }
    
    @staticmethod
    def get_anomalies(db: Session, user_id: int) -> List[Dict]:
        """Get detected anomalies."""
        subscriptions = db.query(Subscription).filter(
            Subscription.user_id == user_id
        ).all()
        
        transactions = db.query(Transaction).filter(
            Transaction.user_id == user_id
        ).all()
        
        subscriptions_data = [
            {
                'id': sub.id,
                'name': sub.name,
                'amount': sub.amount,
                'frequency': sub.frequency
            }
            for sub in subscriptions
        ]
        
        transactions_data = [
            {
                'date': t.date,
                'amount': t.amount,
                'description': t.description,
                'bank_account': t.bank_account
            }
            for t in transactions
        ]
        
        return detect_price_anomalies(subscriptions_data, transactions_data)

