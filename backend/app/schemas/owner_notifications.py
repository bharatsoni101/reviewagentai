from datetime import datetime
from pydantic import BaseModel
class OwnerNotification(BaseModel):
    id: int
    complaint_id: int | None
    type: str
    status: str
    message: str
    created_at: datetime
    sent_at: datetime | None
    complaint_status: str | None = None
    complaint_rating: int | None = None
    complaint_comments: str | None = None
    complaint_customer_name: str | None = None
    complaint_phone_number: str | None = None
class OwnerNotificationList(BaseModel):
    items: list[OwnerNotification]
    total: int
    unread: int
