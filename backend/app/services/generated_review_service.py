from sqlalchemy.orm import Session

from backend.app.models.generated_review import GeneratedPositiveReview
from backend.app.models.review_session import ReviewSession
from backend.app.services.ai_review_service import AIReviewService


class GeneratedReviewService:

    @staticmethod
    def generate_positive_reviews(
        db: Session,
        session_id: str,
        customer_input: str,
    ) -> tuple[ReviewSession, list[GeneratedPositiveReview]]:
        review_session = db.get(ReviewSession, session_id)

        if review_session is None:
            raise ValueError("Review session not found")

        if review_session.rating is None:
            raise ValueError("Review session has not been rated")

        if review_session.rating < 4:
            raise ValueError("Positive reviews are available only for ratings 4 or 5")

        generated_reviews = AIReviewService.generate_reviews(
            customer_input=customer_input,
            rating=review_session.rating,
        )

        reviews = [
            GeneratedPositiveReview(
                business_id=review_session.business_id,
                rating=review_session.rating,
                customer_input=customer_input,
                generated_review=generated_review,
            )
            for generated_review in generated_reviews
        ]

        db.add_all(reviews)
        db.commit()

        for review in reviews:
            db.refresh(review)

        return review_session, reviews
