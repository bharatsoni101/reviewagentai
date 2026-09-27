from sqlalchemy import inspect

from backend.app.db.base import Base
from backend.app.db.database import engine
from backend.app.db.seed import seed_demo_data
from backend.app.models import (
    Business,
    SocialLink,
    LocalComplaint,
    GeneratedPositiveReview,
    ReviewEvent,
    Notification,
    ReviewSession,
    FallbackReviewComment,
    User,
    Subscription,
    BillingPayment,
    SubscriptionPlan,
)

EXPECTED_TABLES = {
    "businesses",
    "social_links",
    "local_complaints",
    "generated_positive_reviews",
    "review_events",
    "notifications",
    "review_sessions",
    "fallback_review_comments",
    "users",
    "subscriptions",
    "billing_payments",
    "subscription_plans",
}

def initialize_database() -> None:
    # Remove the legacy audit_logs table from databases created by older versions.
    with engine.begin() as connection:
        connection.exec_driver_sql("DROP TABLE IF EXISTS audit_logs")

    Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    missing_tables = EXPECTED_TABLES - existing_tables

    if missing_tables:
        raise RuntimeError(
            f"Database initialization failed. Missing tables: {sorted(missing_tables)}"
        )

    seed_demo_data()

if __name__ == "__main__":
    initialize_database()
    print("reviewagentai database initialized successfully.")
