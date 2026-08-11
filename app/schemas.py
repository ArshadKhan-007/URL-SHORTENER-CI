"""Pydantic schemas for request validation and response serialization."""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, HttpUrl, ConfigDict


# ---------- Shorten ----------

class ShortenRequest(BaseModel):
    url: HttpUrl
    custom_alias: Optional[str] = None
    expires_at: Optional[datetime] = None


class ShortenResponse(BaseModel):
    short_code: str
    short_url: str
    original_url: str

    model_config = ConfigDict(from_attributes=True)


# ---------- Bulk Shorten ----------

class BulkShortenRequest(BaseModel):
    urls: List[ShortenRequest]


class BulkShortenResponse(BaseModel):
    results: List[ShortenResponse]


# ---------- Stats ----------

class StatsResponse(BaseModel):
    short_code: str
    original_url: str
    click_count: int
    created_at: datetime
    expires_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ---------- Health ----------

class HealthResponse(BaseModel):
    status: str
    database: str
