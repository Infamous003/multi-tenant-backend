from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import Session

from app.api.deps import require_admin_api_key, require_tenant_api_key
from app.db.db import get_db
from app.schemas.tenants import TenantRead
from app.services.usage import UsageService
from app.domain.exceptions import TenantNotFound
from sqlalchemy.exc import SQLAlchemyError
from app.domain.exceptions import QuotaExceeded

router = APIRouter(
    prefix="/usage",
    tags=["Tenant's Usage"],
)

@router.post(
    "/{tenant_id}/reset",
    status_code=status.HTTP_200_OK,
    response_model=TenantRead,
    dependencies=[Depends(require_admin_api_key)],
)
def reset_tenant_usage(tenant_id: int, db: Session = Depends(get_db)):
    """
    Reset a tenant's current usage to 0.

    Args:
        tenant_id (int): ID of the tenant whose usage is to be reset.
        db (Session): SQLModel session for database operations.
    
    Returns:
        TenantRead: The tenant with reset usage.
    
    Raises:
        HTTPException: 404 if tenant is not found.
        HTTPException: 500 if resetting tenant usage fails.
    """
    
    service = UsageService(db)

    try:
        tenant = service.reset_monthly_usage(tenant_id)
    except TenantNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Tenant not found"
        )
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Could not reset tenant usage"
        )

    return tenant

@router.get(
    "/",
    response_model=TenantRead,
    status_code=status.HTTP_200_OK,
)
def get_tenant_usage(tenant_id: int = Depends(require_tenant_api_key), db: Session = Depends(get_db)):
    """
    Get a tenant's current usage.

    Args:
        tenant_id (int): ID of the tenant whose usage is to be retrieved.
        db (Session): SQLModel session for database operations.
    
    Returns:
        TenantRead: The tenant with current usage.
    
    Raises:
        HTTPException: 404 if tenant is not found.
        HTTPException: 500 if retrieving tenant usage fails.
    """

    service = UsageService(db)

    try:
        tenant = service.get_tenant_usage(tenant_id)
    except TenantNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Tenant not found"
        )
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Could not retrieve tenant usage"
        )

    return tenant

@router.post(
    "/usage/increment",
    response_model=TenantRead,
    status_code=status.HTTP_200_OK,
)
def increment_tenant_usage(
    tenant_id: int = Depends(require_tenant_api_key),
    amount: int = 1,
    db: Session = Depends(get_db),
):
    """
    Increment a tenant's current usage by a specified amount.

    Args:
        tenant_id (int): ID of the tenant whose usage is to be incremented.
        amount (int): Amount to increment the usage by (default is 1).
        db (Session): SQLModel session for database operations.
    
    Returns:
        TenantRead: The tenant with updated usage.
    
    Raises:
        HTTPException: 404 if tenant is not found.
        HTTPException: 403 if tenant's quota is exceeded.
        HTTPException: 500 if incrementing tenant usage fails.
    """

    if amount < 1: amount = 1
    service = UsageService(db)

    try:
        tenant = service.increment_tenant_usage(tenant_id, amount)
    except TenantNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Tenant not found"
        )
    except QuotaExceeded:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Tenant quota exceeded"
        )
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Could not increment tenant usage"
        )

    return tenant