from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import Session

from app.api.deps import require_admin_api_key
from app.db.db import get_db
from app.schemas.tenants import TenantCreate, TenantCreateResponse, TenantRead, TenantUpdate
from app.services.usage import UsageService
from app.domain.exceptions import TenantNotFound
from sqlalchemy.exc import SQLAlchemyError

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