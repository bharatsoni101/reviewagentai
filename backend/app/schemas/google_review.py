from datetime import datetime

from pydantic import BaseModel, Field


class SelectReviewRequest(BaseModel):
    review_id: int = Field(..., gt=0, description="ID of the generated review to select")


class GoogleReviewSelectionResponse(BaseModel):
    session_id: str
    business_id: str
    rating: int
    selected_review_id: int
    review_text: str
    google_review_url: str
    status: str
    updated_at: datetime
