from sqlmodel import SQLModel, Field
from sqlalchemy import Column, DateTime
from datetime import datetime, timezone


class Tenant(SQLModel, table=True):
    """
    Represents a tenant in the system.

    Attributes:
        id (int | None): Primary key for the tenant.
        plan_name (str): Name of the tenant's plan.
        monthly_usage_limit (int): Maximum allowed usage per month.
        current_usage (int): Current usage of the tenant.
        period_start (datetime): Start of the usage period.
        period_end (datetime): End of the usage period.
        created_at (datetime): Timestamp when the tenant was created.
        updated_at (datetime): Timestamp when the tenant was last updated.
    """

    __tablename__ = "tenants"

    id: int | None = Field(default=None, primary_key=True)

    plan_name: str = Field(nullable=False)

    monthly_usage_limit: int = Field(nullable=False)

    current_usage: int = Field(default=0, nullable=False)

    period_start: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )

    period_end: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )

    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False),
        default_factory=lambda: datetime.now(timezone.utc),
    )

    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            onupdate=lambda: datetime.now(timezone.utc),
        ),
        default_factory=lambda: datetime.now(timezone.utc),
    )
