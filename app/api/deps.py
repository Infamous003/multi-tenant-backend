from fastapi import HTTPException, Security, status, Depends
from fastapi.security import APIKeyHeader
from ..core.config import settings
from sqlmodel import Session, select
from app.db.db import get_db
from app.db.models.api_key import APIKey
from app.core.security import hash_api_key

api_key_header = APIKeyHeader(
    name="X-API-KEY",
    auto_error=False,
)


def require_admin_api_key(api_key: str | None = Security(api_key_header)) -> None:
    """
    Dependency to validate admin API key.

    Args:
        api_key (str | None): API key provided in X-API-KEY header.

    Raises:
        HTTPException: 401 if admin API key is missing.
        HTTPException: 403 if admin API key is invalid.
    """

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing admin API key",
        )

    if api_key != settings.ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid admin API key",
        )
    
def require_tenant_api_key(
    api_key: str | None = Security(api_key_header),
    db: Session = Depends(get_db),
) -> int:
    """
    Validate the tenant API key and return the associated tenant ID.

    Args:
        api_key (str | None): API key provided in the request header.
        db (Session): SQLModel session for database operations.
    
    Returns:
        int: Tenant ID associated with the valid API key.
    
    Raises:
        HTTPException: 401 if API key is missing.
        HTTPException: 403 if API key is invalid.
    """

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
        )
    
    query = select(APIKey.tenant_id).where(APIKey.api_key_hash == hash_api_key(api_key))
    
    tenant_id = db.exec(query).first()

    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )

    return tenant_id