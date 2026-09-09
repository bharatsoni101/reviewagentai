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
from backend.app.schemas.google_review import (
    GoogleReviewSelectionResponse,
    SelectReviewRequest,
)
from backend.app.services.google_review_service import GoogleReviewService
from backend.app.schemas.private_feedback import (
    PrivateFeedbackRequest,
    PrivateFeedbackResponse,
)
from backend.app.services.private_feedback_service import PrivateFeedbackService

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

        if message == "Groq API key is not configured":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=message,
            )

        if message.startswith("Groq"):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
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


@router.post(
    "/session/{session_id}/private-feedback",
    response_model=PrivateFeedbackResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_private_feedback(
    session_id: str,
    request: PrivateFeedbackRequest,
    db: Session = Depends(get_db),
):
    try:
        review_session, complaint, acknowledgement = (
            PrivateFeedbackService.submit_feedback(
                db=db,
                session_id=session_id,
                comments=request.comments,
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
            status_code=status.HTTP_409_CONFLICT,
            detail=message,
        )

    return PrivateFeedbackResponse(
        session_id=review_session.id,
        business_id=review_session.business_id,
        complaint_id=complaint.id,
        rating=review_session.rating,
        status=review_session.status,
        acknowledgement=acknowledgement,
        created_at=complaint.created_at,
    )


@router.post(
    "/session/{session_id}/google-review/select",
    response_model=GoogleReviewSelectionResponse,
)
def select_google_review(
    session_id: str,
    request: SelectReviewRequest,
    db: Session = Depends(get_db),
):
    try:
        review_session, review, business = GoogleReviewService.select_review(
            db=db,
            session_id=session_id,
            review_id=request.review_id,
        )
    except ValueError as exc:
        message = str(exc)

        if message in {"Review session not found", "Generated review not found", "Business not found"}:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=message,
        )

    return GoogleReviewSelectionResponse(
        session_id=review_session.id,
        business_id=review_session.business_id,
        rating=review_session.rating,
        selected_review_id=review.id,
        review_text=review.generated_review,
        google_review_url=business.google_review_url,
        status=review_session.status,
        updated_at=review_session.updated_at,
    )
