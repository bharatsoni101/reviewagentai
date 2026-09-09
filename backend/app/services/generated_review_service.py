from sqlalchemy.orm import Session

from backend.app.models.generated_review import GeneratedPositiveReview
from backend.app.models.review_session import ReviewSession


class GeneratedReviewService:

    @staticmethod
    def generate_positive_reviews(
        db: Session,
        session_id: str,
        customer_input: str,
    ) -> tuple[ReviewSession, list[GeneratedPositiveReview]]:

        review_session = db.get(
            ReviewSession,
            session_id,
        )

        if review_session is None:
            raise ValueError("Review session not found")

        if review_session.rating is None:
            raise ValueError("Review session has not been rated")

        if review_session.rating < 4:
            raise ValueError(
                "Positive reviews are available only for ratings 4 or 5"
            )

        business_id = review_session.business_id
        rating = review_session.rating

        reviews = [
            GeneratedPositiveReview(
                business_id=business_id,
                rating=rating,
                customer_input=customer_input,
                generated_review=(
                    f"Great experience! {customer_input.strip()} "
                    "The service was excellent and I would definitely "
                    "recommend this place to others."
                ),
            ),
            GeneratedPositiveReview(
                business_id=business_id,
                rating=rating,
                customer_input=customer_input,
                generated_review=(
                    f"Really enjoyed my experience! {customer_input.strip()} "
                    "Everything was smooth, friendly, and enjoyable. "
                    "I would definitely come back again."
                ),
            ),
            GeneratedPositiveReview(
                business_id=business_id,
                rating=rating,
                customer_input=customer_input,
                generated_review=(
                    f"Excellent experience! {customer_input.strip()} "
                    "The overall service was fantastic and exceeded my "
                    "expectations. Highly recommended!"
                ),
            ),
        ]

        db.add_all(reviews)
        db.commit()

        for review in reviews:
            db.refresh(review)

        return review_session, reviews