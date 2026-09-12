from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.core.config import settings
from backend.app.schemas.dashboard import DashboardResponse
from backend.app.services.dashboard_service import DashboardService



def require_business_api_key(x_business_api_key: str | None = Header(default=None)) -> None:
    if settings.app_env.lower() in {"production", "prod"}:
        if not settings.business_api_key or x_business_api_key != settings.business_api_key:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Business API key required")

router = APIRouter(prefix="/dashboard", tags=["Dashboard"], dependencies=[Depends(require_business_api_key)])


@router.get("/business/{slug}", response_model=DashboardResponse)
def get_business_dashboard(
    slug: str,
    days: int | None = Query(default=None, ge=1, le=365),
    db: Session = Depends(get_db),
):
    try:
        return DashboardService.get_business_dashboard(db=db, slug=slug, days=days)
    except ValueError as exc:
        message = str(exc)
        if message == "Business not found":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=message)
