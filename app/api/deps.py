from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from ..core.config import settings

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