from datetime import datetime

from pydantic import BaseModel, Field


class PositiveReviewRequest(BaseModel):
    customer_input: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="Customer's optional review comments",
    )


class GeneratedReviewItem(BaseModel):
    id: int
    generated_review: str
    selected: bool
    created_at: datetime


class PositiveReviewResponse(BaseModel):
    session_id: str
    business_id: str
    rating: int
    generation_source: str
    reviews: list[GeneratedReviewItem]