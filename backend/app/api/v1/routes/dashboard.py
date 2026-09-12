from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.schemas.dashboard import DashboardResponse
from backend.app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


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
