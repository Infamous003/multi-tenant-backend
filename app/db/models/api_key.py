from sqlmodel import SQLModel, Field
from sqlalchemy import Column, DateTime, ForeignKey
from datetime import datetime, timezone


class APIKey(SQLModel, table=True):
    """
    Represents an API key associated with a tenant.

    Attributes:
        id (int | None): Primary key for the API key.
        tenant_id (int): Foreign key referencing the associated tenant.
        api_key_hash (str): SHA-256 hash of the API key.
        created_at (datetime): Timestamp when the API key was created.
    """
    
    __tablename__ = "api_keys"

    id: int | None = Field(default=None, primary_key=True)
    
    tenant_id: int = Field(
        sa_column=Column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    )

    api_key_hash: str = Field(nullable=False, unique=True)

    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False),
        default_factory=lambda: datetime.now(timezone.utc),
    )