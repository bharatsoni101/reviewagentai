from sqlalchemy import select

from backend.app.db.database import SessionLocal
from backend.app.models.business import Business
from backend.app.models.social_link import SocialLink

DEMO_BUSINESS = {
    "slug": "abc-restaurant",
    "name": "ABC Restaurant",
    "logo_url": "",
    "description": "Great food. Great service. Always here for you.",
    "category": "Restaurant",
    "google_review_url": "https://search.google.com/local/writereview?placeid=REPLACE_ME",
    "status": "ACTIVE",
}

DEMO_LINKS = [
    ("INSTAGRAM", "https://instagram.com/", 1),
    ("FACEBOOK", "https://facebook.com/", 2),
    ("YOUTUBE", "https://youtube.com/", 3),
    ("WHATSAPP", "https://wa.me/", 4),
    ("LINKEDIN", "https://linkedin.com/", 5),
]

def seed_demo_data() -> None:
    with SessionLocal() as db:
        business = db.scalar(
            select(Business).where(Business.slug == DEMO_BUSINESS["slug"])
        )

        if business is None:
            business = Business(**DEMO_BUSINESS)
            db.add(business)
            db.flush()

        existing_platforms = {
            link.platform
            for link in db.scalars(
                select(SocialLink).where(SocialLink.business_id == business.id)
            ).all()
        }

        for platform, url, display_order in DEMO_LINKS:
            if platform not in existing_platforms:
                db.add(
                    SocialLink(
                        business_id=business.id,
                        platform=platform,
                        url=url,
                        display_order=display_order,
                        enabled=True,
                    )
                )

        db.commit()
