from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime, timezone

class TenantCreate(BaseModel):
    """
    Schemas for creating a new tenant.

    Attributes:
        plan_name (str): Name of the tenant's plan, must be at least 1 character.
        monthly_usage_limit (int): Monthly usage limit for the tenant, must be non-negative.
    """

    plan_name: str = Field(min_length=1)
    monthly_usage_limit: int = Field(ge=0)


class TenantRead(BaseModel):
    """
    Schema for reading a tenant.

    Attributes:
        id (int): Tenant ID.
        plan_name (str): Name of the tenant's plan.
        monthly_usage_limit (int): Maximum allowed usage per month.
        current_usage (int): Current usage of the tenant.
        period_start (datetime): Start of the usage period.
        period_end (datetime): End of the usage period.
        created_at (datetime): Timestamp when the tenant was created.
        updated_at (datetime): Timestamp when the tenant was last updated.
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    plan_name: str
    monthly_usage_limit: int
    current_usage: int
    period_start: datetime
    period_end: datetime
    created_at: datetime
    updated_at: datetime

    @field_validator("period_start", "period_end", "created_at", "updated_at", mode="before")
    def force_utc(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v.astimezone(timezone.utc)


class TenantCreateResponse(BaseModel):
    """
    Response schema for tenant creation.
    Attributes:
        tenant (TenantRead): The created tenant.
        api_key (str): The generated API key for the tenant.
    """
    tenant: TenantRead
    api_key: str


class TenantUpdate(BaseModel):
    """
    Schema for updating a tenant.

    Attributes:
        plan_name (str | None): New plan name (optional).
        monthly_usage_limit (int | None): New monthly usage limit (optional).
    """
    plan_name: str | None = Field(default=None, min_length=1)
    monthly_usage_limit: int | None = Field(default=None, ge=0)