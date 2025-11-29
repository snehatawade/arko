from twilio.rest import Client
from typing import Optional
try:
    from config import settings
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from config import settings
from datetime import datetime, timedelta
from app.models import Subscription, User

class NotificationService:
    """Handle WhatsApp notifications via Twilio."""
    
    def __init__(self):
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            self.enabled = True
        else:
            self.enabled = False
    
    def send_whatsapp(self, phone: str, message: str) -> bool:
        """Send WhatsApp message via Twilio."""
        if not self.enabled:
            print(f"[WhatsApp] Would send to {phone}: {message}")
            return False
        
        try:
            # Format phone number (assuming +91 for India, adjust as needed)
            if not phone.startswith('+'):
                phone = f"+91{phone}"
            
            self.client.messages.create(
                from_=settings.TWILIO_WHATSAPP_FROM,
                to=f"whatsapp:{phone}",
                body=message
            )
            return True
        except Exception as e:
            print(f"Error sending WhatsApp: {e}")
            return False
    
    def check_and_send_renewal_alerts(self, db, user: User):
        """Check for upcoming renewals and send alerts."""
        tomorrow = datetime.now() + timedelta(days=1)
        
        subscriptions = db.query(Subscription).filter(
            Subscription.user_id == user.id,
            Subscription.status == "active"
        ).all()
        
        for sub in subscriptions:
            # Check if renewal is tomorrow (within 24 hours)
            if abs((sub.next_renewal - tomorrow).total_seconds()) < 86400:
                message = f"⚠️ Arko Alert: Your {sub.name} subscription (₹{sub.amount:.2f}) renews tomorrow."
                self.send_whatsapp(user.phone, message)
    
    def send_new_subscription_alert(self, user: User, subscription: Subscription):
        """Alert user about newly detected subscription."""
        message = f"🔔 Arko: New subscription detected - {subscription.name} (₹{subscription.amount:.2f}/{subscription.frequency})"
        self.send_whatsapp(user.phone, message)
    
    def send_price_increase_alert(self, user: User, subscription: Subscription, old_amount: float, new_amount: float):
        """Alert user about price increase."""
        message = f"📈 Arko Alert: {subscription.name} price increased from ₹{old_amount:.2f} to ₹{new_amount:.2f}"
        self.send_whatsapp(user.phone, message)
    
    def send_unusual_activity_alert(self, user: User, description: str):
        """Alert user about unusual activity."""
        message = f"🚨 Arko Alert: Unusual activity detected - {description}"
        self.send_whatsapp(user.phone, message)
    
    def send_harvey_recommendation_alert(self, user: User, recommendation: str):
        """Alert user about Harvey recommendation."""
        message = f"💡 Harvey Insight: {recommendation}"
        self.send_whatsapp(user.phone, message)

notification_service = NotificationService()

