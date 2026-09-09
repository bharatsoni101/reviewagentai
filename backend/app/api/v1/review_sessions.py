from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.database import get_db

from backend.app.schemas.review_session import (
    ReviewSessionCreate,
    ReviewSessionResponse,
)
from backend.app.services.review_session_service import (
    ReviewSessionService,
)

from backend.app.schemas.review_rating import (
    ReviewRatingRequest,
    ReviewRatingResponse,
)

from backend.app.schemas.generated_review import (
    GeneratedReviewItem,
    PositiveReviewRequest,
    PositiveReviewResponse,
)

from backend.app.services.generated_review_service import (
    GeneratedReviewService,
)

router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"],
)


@router.post(
    "/session",
    response_model=ReviewSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_review_session(
    request: ReviewSessionCreate,
    db: Session = Depends(get_db),
):
    try:
        review_session = ReviewSessionService.create_session(
            db=db,
            business_slug=request.business_slug,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    return ReviewSessionResponse(
        session_id=review_session.id,
        business_id=review_session.business_id,
        business_slug=request.business_slug,
        status=review_session.status,
        created_at=review_session.created_at,
    )

@router.post(
    "/session/{session_id}/rating",
    response_model=ReviewRatingResponse,
)
def rate_review_session(
    session_id: str,
    request: ReviewRatingRequest,
    db: Session = Depends(get_db),
):
    try:
        review_session = ReviewSessionService.rate_session(
            db=db,
            session_id=session_id,
            rating=request.rating,
        )
    except ValueError as exc:
        message = str(exc)

        if message == "Review session not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=message,
        )

    if request.rating >= 4:
        next_step = "positive_review"
    else:
        next_step = "private_feedback"

    return ReviewRatingResponse(
        session_id=review_session.id,
        business_id=review_session.business_id,
        rating=review_session.rating,
        status=review_session.status,
        next_step=next_step,
        updated_at=review_session.updated_at,
    )

@router.post(
    "/session/{session_id}/positive-reviews",
    response_model=PositiveReviewResponse,
)
def generate_positive_reviews(
    session_id: str,
    request: PositiveReviewRequest,
    db: Session = Depends(get_db),
):
    try:
        review_session, reviews = (
            GeneratedReviewService.generate_positive_reviews(
                db=db,
                session_id=session_id,
                customer_input=request.customer_input,
            )
        )

    except ValueError as exc:
        message = str(exc)

        if message == "Review session not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )

    return PositiveReviewResponse(
        session_id=review_session.id,
        business_id=review_session.business_id,
        rating=review_session.rating,
        reviews=[
            GeneratedReviewItem(
                id=review.id,
                generated_review=review.generated_review,
                selected=review.selected,
                created_at=review.created_at,
            )
            for review in reviews
        ],
    )

