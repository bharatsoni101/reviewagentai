from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.db.database import get_db
from backend.app.schemas.notification import (
    NotificationListResponse,
    NotificationResponse,
    NotificationRetryResponse,
    NotificationStatusUpdate,
)
from backend.app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])


def require_business_api_key(x_business_api_key: str | None = Header(default=None)) -> None:
    # Development remains convenient; production requires an explicit secret.
    if settings.app_env.lower() in {"production", "prod"}:
        if not settings.business_api_key or x_business_api_key != settings.business_api_key:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Business API key required")


def _item(notification) -> NotificationResponse:
    return NotificationResponse.model_validate(notification, from_attributes=True)


@router.get("/business/{slug}", response_model=NotificationListResponse, dependencies=[Depends(require_business_api_key)])
def list_notifications(
    slug: str,
    status_filter: str | None = Query(default=None, alias="status", pattern="^(PENDING|PROCESSING|SENT|FAILED)$"),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    try:
        items, total = NotificationService.list_for_business(db, slug, status_filter, limit)
    except ValueError as exc:
        code = status.HTTP_404_NOT_FOUND if str(exc) == "Business not found" else status.HTTP_409_CONFLICT
        raise HTTPException(status_code=code, detail=str(exc))
    return NotificationListResponse(items=[_item(item) for item in items], total=total)


@router.patch("/{notification_id}", response_model=NotificationResponse, dependencies=[Depends(require_business_api_key)])
def update_notification(
    notification_id: int,
    request: NotificationStatusUpdate,
    db: Session = Depends(get_db),
):
    try:
        return _item(NotificationService.update_status(db, notification_id, request.status))
    except ValueError as exc:
        message = str(exc)
        code = status.HTTP_404_NOT_FOUND if message == "Notification not found" else status.HTTP_409_CONFLICT
        raise HTTPException(status_code=code, detail=message)


@router.post("/{notification_id}/retry", response_model=NotificationRetryResponse, dependencies=[Depends(require_business_api_key)])
def retry_notification(notification_id: int, db: Session = Depends(get_db)):
    try:
        return _item(NotificationService.retry(db, notification_id))
    except ValueError as exc:
        message = str(exc)
        code = status.HTTP_404_NOT_FOUND if message == "Notification not found" else status.HTTP_409_CONFLICT
        raise HTTPException(status_code=code, detail=message)
