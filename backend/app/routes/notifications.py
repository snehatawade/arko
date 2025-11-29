from fastapi import APIRouter, Depends
from app.models import User
from app.routes.auth import get_current_user
from app.services.notifications import notification_service
from pydantic import BaseModel

router = APIRouter(prefix="/notify", tags=["notifications"])

class WhatsAppMessage(BaseModel):
    message: str

@router.post("/whatsapp")
def send_whatsapp(
    message_data: WhatsAppMessage,
    current_user: User = Depends(get_current_user)
):
    """Send a test WhatsApp message."""
    success = notification_service.send_whatsapp(
        current_user.phone,
        message_data.message
    )
    return {"success": success, "message": "WhatsApp sent" if success else "WhatsApp service not configured"}

