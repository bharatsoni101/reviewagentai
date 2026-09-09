from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.business import Business
from backend.app.models.review_session import ReviewSession


class ReviewSessionService:

    @staticmethod
    def create_session(
        db: Session,
        business_slug: str,
    ) -> ReviewSession:
        business = db.scalar(
            select(Business).where(
                Business.slug == business_slug
            )
        )

        if business is None:
            raise ValueError("Business not found")

        review_session = ReviewSession(
            business_id=business.id,
            status="started",
        )

        db.add(review_session)
        db.commit()
        db.refresh(review_session)

        return review_session

    @staticmethod
    def rate_session(
        db: Session,
        session_id: str,
        rating: int,
    ) -> ReviewSession:
        review_session = db.get(
            ReviewSession,
            session_id,
        )

        if review_session is None:
            raise ValueError("Review session not found")

        if review_session.status != "started":
            raise ValueError("Review session has already been rated")

        review_session.rating = rating
        review_session.status = "rated"

        db.commit()
        db.refresh(review_session)

        return review_session