from sqlalchemy import delete, select

from backend.app.db.database import SessionLocal
from backend.app.models.business import Business
from backend.app.models.social_link import SocialLink

REVIEWAGENTAI_BUSINESS = {
    "slug": "reviewagentai",
    "name": "ReviewAgentAI",
    "logo_url": "/logos/reviewagentai.jpg",
    "description": "ReviewAgentAI is an AI-powered platform that helps businesses generate authentic customer reviews and feedback. Our advanced AI algorithms analyze customer interactions and provide valuable insights to improve your business reputation and customer satisfaction.",
    "category": "AI & Technology",
    "google_review_url": "https://search.google.com/local/writereview?placeid=ChIJV0S728r9YjkRBfIuWZfvmZ8",
    "status": "ACTIVE",
}

LEGACY_DEMO_BUSINESS = {
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


def _seed_business(db, business_data: dict) -> None:
    business = db.scalar(
        select(Business).where(Business.slug == business_data["slug"])
    )

    if business is None:
        business = Business(**business_data)
        db.add(business)
        db.flush()
    else:
        # Keep the demo business itself in sync when seed data changes.
        for field, value in business_data.items():
            if getattr(business, field) != value:
                setattr(business, field, value)

    # Demo social links are controlled by the seed. Remove old/test links for
    # the demo business so repeated application startups cannot accumulate
    # duplicate or obsolete records.
    canonical_platforms = {platform for platform, _, _ in DEMO_LINKS}
    existing_links = db.scalars(
        select(SocialLink)
        .where(SocialLink.business_id == business.id)
        .order_by(SocialLink.id)
    ).all()

    first_by_platform: dict[str, SocialLink] = {}
    for link in existing_links:
        if link.platform not in canonical_platforms:
            db.delete(link)
            continue
        if link.platform in first_by_platform:
            db.delete(link)
            continue
        first_by_platform[link.platform] = link

    for platform, url, display_order in DEMO_LINKS:
        link = first_by_platform.get(platform)
        if link is None:
            db.add(
                SocialLink(
                    business_id=business.id,
                    platform=platform,
                    url=url,
                    display_order=display_order,
                    enabled=True,
                )
            )
        else:
            # Repair an existing canonical record instead of creating another.
            link.url = url
            link.display_order = display_order
            link.enabled = True


def seed_demo_data() -> None:
    with SessionLocal() as db:
        _seed_business(db, REVIEWAGENTAI_BUSINESS)
        # Keep the original demo business for backward-compatible tests/examples.
        _seed_business(db, LEGACY_DEMO_BUSINESS)
        db.commit()
