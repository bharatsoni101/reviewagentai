from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class SocialLinkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    platform: str
    url: str
    display_order: int
    enabled: bool

class BusinessResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    slug: str
    name: str
    logo_url: str | None
    description: str | None
    category: str | None
    google_review_url: str
    status: str
    created_at: datetime
    updated_at: datetime
    social_links: list[SocialLinkResponse] = Field(default_factory=list)
