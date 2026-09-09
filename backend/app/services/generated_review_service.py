from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.business import Business
from backend.app.models.fallback_review_comment import FallbackReviewComment
from backend.app.models.generated_review import GeneratedPositiveReview
from backend.app.models.review_session import ReviewSession
from backend.app.services.ai_review_service import AIReviewService, ReviewGenerationResult
from backend.app.services.review_session_service import ReviewSessionService


class GeneratedReviewService:

    @staticmethod
    def _get_fallback_templates(db: Session, business_id: int, rating: int) -> list[str]:
        rows = db.scalars(
            select(FallbackReviewComment)
            .where(
                FallbackReviewComment.business_id == business_id,
                FallbackReviewComment.rating == rating,
                FallbackReviewComment.enabled.is_(True),
            )
            .order_by(FallbackReviewComment.display_order, FallbackReviewComment.id)
        ).all()
        return [row.comment for row in rows]

    @staticmethod
    def generate_positive_reviews(
        db: Session,
        session_id: str,
        customer_input: str,
    ) -> tuple[ReviewSession, list[GeneratedPositiveReview], str]:
        review_session = ReviewSessionService.validate_active_session(db, session_id)

        if review_session.rating is None:
            raise ValueError("Review session has not been rated")

        if review_session.rating < 4:
            raise ValueError("Positive reviews are available only for ratings 4 or 5")

        business = db.get(Business, int(review_session.business_id))
        if business is None:
            raise ValueError("Business not found")

        fallback_templates = GeneratedReviewService._get_fallback_templates(
            db, business.id, review_session.rating
        )
        if not fallback_templates:
            raise ValueError(
                f"No fallback review comments are configured for rating {review_session.rating}"
            )

        if business.prefer_ai_comments:
            result = AIReviewService.generate_reviews(
                customer_input=customer_input,
                rating=review_session.rating,
                fallback_templates=fallback_templates,
            )
        else:
            result = AIReviewService._render_fallback_reviews(
                customer_input, fallback_templates
            )
            result = ReviewGenerationResult(result, "fallback")

        reviews = [
            GeneratedPositiveReview(
                business_id=review_session.business_id,
                rating=review_session.rating,
                customer_input=customer_input,
                generated_review=generated_review,
            )
            for generated_review in result.reviews
        ]

        db.add_all(reviews)
        db.commit()

        for review in reviews:
            db.refresh(review)

        return review_session, reviews, result.source
