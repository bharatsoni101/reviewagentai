from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.core.config import settings
from backend.app.schemas.analytics import AnalyticsResponse
from backend.app.services.analytics_service import AnalyticsService



def require_business_api_key(x_business_api_key: str | None = Header(default=None)) -> None:
    if settings.app_env.lower() in {"production", "prod"}:
        if not settings.business_api_key or x_business_api_key != settings.business_api_key:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Business API key required")

router = APIRouter(prefix="/analytics", tags=["Analytics"], dependencies=[Depends(require_business_api_key)])


@router.get("/business/{slug}", response_model=AnalyticsResponse)
def get_business_analytics(
    slug: str,
    days: int | None = Query(default=None, ge=1, le=365),
    db: Session = Depends(get_db),
):
    try:
        return AnalyticsService.get_business_analytics(db=db, slug=slug, days=days)
    except ValueError as exc:
        message = str(exc)
        if message == "Business not found":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=message)
