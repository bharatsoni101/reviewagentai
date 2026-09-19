import json
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from backend.app.core.security import require_admin
from backend.app.db.database import get_db
from backend.app.models.business import Business
from backend.app.models.complaint import LocalComplaint
from backend.app.models.generated_review import GeneratedPositiveReview
from backend.app.models.review_event import ReviewEvent
from backend.app.models.social_link import SocialLink
from backend.app.models.subscription import Subscription
from backend.app.models.user import User
from backend.app.schemas.admin_business import (
    AdminBusinessCreate, AdminBusinessDetail, AdminBusinessListItem,
    AdminBusinessListResponse, AdminBusinessUpdate, AdminSocialLink,
)
from backend.app.services.billing_service import BillingService

router = APIRouter(prefix="/admin/businesses", tags=["admin-businesses"])


def _owner(db: Session, owner_user_id: int | None) -> User | None:
    if owner_user_id is None:
        return None
    user = db.get(User, owner_user_id)
    if user is None:
        raise HTTPException(404, "Business owner user not found", headers={"X-Error-Code": "OWNER_NOT_FOUND"})
    if user.role != "BUSINESS_OWNER":
        raise HTTPException(422, "Selected user is not a business owner", headers={"X-Error-Code": "OWNER_ROLE_REQUIRED"})
    if not user.is_active:
        raise HTTPException(422, "Selected business owner is inactive", headers={"X-Error-Code": "OWNER_INACTIVE"})
    return user


def _validate_slug(db: Session, slug: str, current_id: int | None = None) -> None:
    q = select(Business).where(Business.slug == slug)
    if current_id is not None:
        q = q.where(Business.id != current_id)
    if db.scalar(q) is not None:
        raise HTTPException(409, "A business with this slug already exists", headers={"X-Error-Code": "BUSINESS_SLUG_EXISTS"})


def _set_owner(db: Session, business: Business, owner_user_id: int | None) -> None:
    if owner_user_id is None:
        for user in business.users:
            if user.role == "BUSINESS_OWNER" and user.business_id == business.id:
                user.business_id = None
        return
    owner = _owner(db, owner_user_id)
    if owner.business_id is not None and owner.business_id != business.id:
        raise HTTPException(409, "This owner is already assigned to another business", headers={"X-Error-Code": "OWNER_ALREADY_ASSIGNED"})
    for user in business.users:
        if user.id != owner.id and user.role == "BUSINESS_OWNER":
            user.business_id = None
    owner.business_id = business.id


def _replace_social_links(db: Session, business: Business, links: list[AdminSocialLink]) -> None:
    business.social_links[:] = []
    db.flush()
    for link in links:
        db.add(SocialLink(business_id=business.id, **link.model_dump()))


def _customer_settings(business: Business) -> dict[str, object]:
    try:
        value = json.loads(business.customer_settings_json or "{}")
        return value if isinstance(value, dict) else {}
    except json.JSONDecodeError:
        return {}


def _stats(db: Session, business_id: int):
    review_count = int(db.scalar(select(func.count(GeneratedPositiveReview.id)).where(GeneratedPositiveReview.business_id == business_id)) or 0)
    complaint_count = int(db.scalar(select(func.count(LocalComplaint.id)).where(LocalComplaint.business_id == business_id)) or 0)
    avg = db.scalar(select(func.avg(ReviewEvent.rating)).where(ReviewEvent.business_id == business_id, ReviewEvent.rating.is_not(None)))
    return review_count, complaint_count, round(float(avg), 2) if avg is not None else None


def _detail(db: Session, business: Business) -> AdminBusinessDetail:
    owner = next((u for u in business.users if u.role == "BUSINESS_OWNER" and u.business_id == business.id), None)
    sub = BillingService.subscription(db, business.id)
    review_count, complaint_count, average_rating = _stats(db, business.id)
    return AdminBusinessDetail(
        id=business.id, slug=business.slug, name=business.name, logo_url=business.logo_url,
        description=business.description, category=business.category,
        google_review_pc_url=business.google_review_pc_url, google_review_mob_url=business.google_review_mob_url,
        status=business.status, prefer_ai_comments=business.prefer_ai_comments,
        brand_primary_color=business.brand_primary_color, brand_secondary_color=business.brand_secondary_color,
        welcome_message=business.welcome_message, nfc_enabled=business.nfc_enabled, qr_enabled=business.qr_enabled,
        customer_settings=_customer_settings(business), owner_user_id=owner.id if owner else None,
        owner_name=owner.full_name if owner else None, owner_email=owner.email if owner else None,
        social_links=[AdminSocialLink.model_validate(x) for x in business.social_links],
        plan=sub.plan, subscription_status=sub.status, trial_ends_at=sub.trial_ends_at,
        current_period_start=sub.current_period_start, current_period_end=sub.current_period_end,
        cancel_at_period_end=sub.cancel_at_period_end, review_count=review_count,
        complaint_count=complaint_count, average_rating=average_rating,
        created_at=business.created_at, updated_at=business.updated_at,
    )


@router.get("/owners")
def list_business_owners(_admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    users = db.scalars(select(User).where(User.role == "BUSINESS_OWNER", User.is_active.is_(True)).order_by(User.full_name, User.email)).all()
    return [{"id": u.id, "full_name": u.full_name, "email": u.email, "business_id": u.business_id} for u in users]


@router.get("", response_model=AdminBusinessListResponse)
def list_businesses(
    search: str | None = Query(None, max_length=100),
    status_filter: str | None = Query(None, alias="status", pattern="^(ACTIVE|INACTIVE)$"),
    owner_user_id: int | None = Query(None, ge=1),
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    q = select(Business).options(selectinload(Business.users), selectinload(Business.subscription)).order_by(Business.id.desc())
    if status_filter:
        q = q.where(Business.status == status_filter)
    if owner_user_id:
        q = q.join(User, User.business_id == Business.id).where(User.id == owner_user_id)
    if search:
        term = f"%{search.strip()}%"
        q = q.where(or_(Business.name.ilike(term), Business.slug.ilike(term), Business.category.ilike(term)))
    businesses = db.scalars(q).unique().all()
    items = []
    for b in businesses:
        owner = next((u for u in b.users if u.role == "BUSINESS_OWNER" and u.business_id == b.id), None)
        sub = BillingService.subscription(db, b.id)
        review_count, complaint_count, average_rating = _stats(db, b.id)
        items.append(AdminBusinessListItem(
            id=b.id, slug=b.slug, name=b.name, category=b.category, status=b.status,
            owner_user_id=owner.id if owner else None, owner_name=owner.full_name if owner else None,
            owner_email=owner.email if owner else None, plan=sub.plan, subscription_status=sub.status,
            review_count=review_count, complaint_count=complaint_count, average_rating=average_rating,
            created_at=b.created_at, updated_at=b.updated_at,
        ))
    return AdminBusinessListResponse(items=items, total=len(items))


@router.get("/{business_id}", response_model=AdminBusinessDetail)
def get_business_detail(business_id: int, _admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    business = db.scalar(select(Business).options(selectinload(Business.users), selectinload(Business.social_links)).where(Business.id == business_id))
    if business is None:
        raise HTTPException(404, "Business not found", headers={"X-Error-Code": "BUSINESS_NOT_FOUND"})
    return _detail(db, business)


@router.post("", response_model=AdminBusinessDetail, status_code=201)
def create_business(payload: AdminBusinessCreate, _admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    _validate_slug(db, payload.slug)
    owner = _owner(db, payload.owner_user_id)
    if owner and owner.business_id is not None:
        raise HTTPException(409, "This owner is already assigned to another business", headers={"X-Error-Code": "OWNER_ALREADY_ASSIGNED"})
    business = Business(
        slug=payload.slug, name=payload.name.strip(), description=payload.description, category=payload.category,
        logo_url=payload.logo_url, welcome_message=payload.welcome_message,
        google_review_pc_url=payload.google_review_pc_url, google_review_mob_url=payload.google_review_mob_url,
        status=payload.status, prefer_ai_comments=payload.prefer_ai_comments,
        brand_primary_color=payload.brand_primary_color, brand_secondary_color=payload.brand_secondary_color,
        nfc_enabled=payload.nfc_enabled, qr_enabled=payload.qr_enabled,
        customer_settings_json=json.dumps(payload.customer_settings),
    )
    db.add(business); db.flush()
    if owner: owner.business_id = business.id
    _replace_social_links(db, business, payload.social_links)
    db.add(Subscription(business_id=business.id, plan="STARTER", status="TRIALING", provider="MOCK"))
    db.commit(); db.refresh(business)
    business = db.scalar(select(Business).options(selectinload(Business.users), selectinload(Business.social_links)).where(Business.id == business.id))
    return _detail(db, business)


@router.put("/{business_id}", response_model=AdminBusinessDetail)
def update_business(business_id: int, payload: AdminBusinessUpdate, _admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    business = db.scalar(select(Business).options(selectinload(Business.users), selectinload(Business.social_links)).where(Business.id == business_id))
    if business is None:
        raise HTTPException(404, "Business not found", headers={"X-Error-Code": "BUSINESS_NOT_FOUND"})
    data = payload.model_dump(exclude_unset=True)
    if "slug" in data and data["slug"] != business.slug:
        _validate_slug(db, data["slug"], business.id)
    owner_user_id = data.pop("owner_user_id", None) if "owner_user_id" in data else None
    social_links = data.pop("social_links", None) if "social_links" in data else None
    customer_settings = data.pop("customer_settings", None) if "customer_settings" in data else None
    for field, value in data.items():
        setattr(business, field, value)
    if customer_settings is not None:
        business.customer_settings_json = json.dumps(customer_settings)
    if "owner_user_id" in payload.model_fields_set:
        _set_owner(db, business, owner_user_id)
    if social_links is not None:
        _replace_social_links(db, business, social_links)
    db.commit(); db.refresh(business)
    business = db.scalar(select(Business).options(selectinload(Business.users), selectinload(Business.social_links)).where(Business.id == business.id))
    return _detail(db, business)


@router.patch("/{business_id}/status", response_model=AdminBusinessDetail)
def set_business_status(business_id: int, new_status: str = Query(..., pattern="^(ACTIVE|INACTIVE)$"), _admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    business = db.scalar(select(Business).options(selectinload(Business.users), selectinload(Business.social_links)).where(Business.id == business_id))
    if business is None:
        raise HTTPException(404, "Business not found", headers={"X-Error-Code": "BUSINESS_NOT_FOUND"})
    business.status = new_status
    db.commit(); db.refresh(business)
    return _detail(db, business)
