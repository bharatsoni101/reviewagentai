from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator

class AdminSocialLink(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    platform: str = Field(min_length=1, max_length=30)
    url: str = Field(min_length=1, max_length=2000)
    display_order: int = Field(default=0, ge=0, le=1000)
    enabled: bool = True

class AdminBusinessCreate(BaseModel):
    slug: str = Field(min_length=2, max_length=100, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    name: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    category: str | None = Field(default=None, max_length=100)
    logo_url: str | None = Field(default=None, max_length=1000)
    welcome_message: str | None = Field(default=None, max_length=1000)
    google_review_pc_url: str = Field(min_length=1, max_length=2000)
    google_review_mob_url: str = Field(min_length=1, max_length=2000)
    status: str = Field(default="ACTIVE", pattern=r"^(ACTIVE|INACTIVE)$")
    prefer_ai_comments: bool = True
    brand_primary_color: str = Field(default="#4f46e5", pattern=r"^#[0-9A-Fa-f]{6}$")
    brand_secondary_color: str = Field(default="#312e81", pattern=r"^#[0-9A-Fa-f]{6}$")
    nfc_enabled: bool = True
    qr_enabled: bool = True
    customer_settings: dict[str, object] = Field(default_factory=dict)
    owner_user_id: int | None = Field(default=None, ge=1)
    social_links: list[AdminSocialLink] = Field(default_factory=list, max_length=30)

class AdminBusinessUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    slug: str | None = Field(default=None, min_length=2, max_length=100, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    description: str | None = Field(default=None, max_length=2000)
    category: str | None = Field(default=None, max_length=100)
    logo_url: str | None = Field(default=None, max_length=1000)
    welcome_message: str | None = Field(default=None, max_length=1000)
    google_review_pc_url: str | None = Field(default=None, min_length=1, max_length=2000)
    google_review_mob_url: str | None = Field(default=None, min_length=1, max_length=2000)
    status: str | None = Field(default=None, pattern=r"^(ACTIVE|INACTIVE)$")
    prefer_ai_comments: bool | None = None
    brand_primary_color: str | None = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")
    brand_secondary_color: str | None = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")
    nfc_enabled: bool | None = None
    qr_enabled: bool | None = None
    customer_settings: dict[str, object] | None = None
    owner_user_id: int | None = Field(default=None, ge=1)
    social_links: list[AdminSocialLink] | None = Field(default=None, max_length=30)

class AdminBusinessListItem(BaseModel):
    id: int
    slug: str
    name: str
    category: str | None
    status: str
    owner_user_id: int | None
    owner_name: str | None
    owner_email: str | None
    plan: str
    subscription_status: str
    review_count: int
    complaint_count: int
    average_rating: float | None
    created_at: datetime
    updated_at: datetime

class AdminBusinessListResponse(BaseModel):
    items: list[AdminBusinessListItem]
    total: int

class AdminBusinessDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    slug: str
    name: str
    logo_url: str | None
    description: str | None
    category: str | None
    google_review_pc_url: str
    google_review_mob_url: str
    status: str
    prefer_ai_comments: bool
    brand_primary_color: str
    brand_secondary_color: str
    welcome_message: str | None
    nfc_enabled: bool
    qr_enabled: bool
    customer_settings: dict[str, object]
    owner_user_id: int | None
    owner_name: str | None
    owner_email: str | None
    social_links: list[AdminSocialLink]
    plan: str
    subscription_status: str
    trial_ends_at: datetime | None
    current_period_start: datetime | None
    current_period_end: datetime | None
    cancel_at_period_end: bool
    review_count: int
    complaint_count: int
    average_rating: float | None
    created_at: datetime
    updated_at: datetime
