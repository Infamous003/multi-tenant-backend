from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import Session

from app.api.deps import require_admin_api_key
from app.db.db import get_db
from app.schemas.tenants import TenantCreate, TenantCreateResponse, TenantRead, TenantUpdate
from app.services.tenant import TenantService
from app.domain.exceptions import TenantNotFound
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter(
    prefix="/tenants",
    tags=["Tenants"],
)

@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=TenantCreateResponse,
    dependencies=[Depends(require_admin_api_key)],
)
def create_tenant(
    payload: TenantCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new tenant.

    Args:
        payload (TenantCreate): Data for the new tenant.
        db (Session): Database session.

    Returns:
        TenantResponse: The created tenant and its API key.
    """

    tenant_service = TenantService(db)
    tenant, api_key = tenant_service.create_tenant(payload)

    return TenantCreateResponse(
        tenant=tenant,
        api_key=api_key,
)

@router.put(
    "/{tenant_id}",
    status_code=status.HTTP_200_OK,
    response_model=TenantRead,
    dependencies=[Depends(require_admin_api_key)],
)
def update_tenant(
    tenant_id: int,
    payload: TenantUpdate,
    db: Session = Depends(get_db),
):
    """
    Update an existing tenant's plan name and/or monthly usage limit.

    Args:
        tenant_id (int): ID of the tenant to update.
        payload (TenantUpdate): Payload containing updated plan name and/or monthly usage limit.
        db (Session): SQLModel session for DB operations.

    Returns:
        TenantRead: The updated tenant.
    
    Raises:
        HTTPException: 400 if no fields to update are provided.
        HTTPException: 404 if tenant is not found.
        HTTPException: 500 if tenant update fails.
    """

    service = TenantService(db)
    if payload.plan_name is None and payload.monthly_usage_limit is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

    try:
        tenant = service.update_tenant_usage(tenant_id, payload)
    except TenantNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Tenant not found"
        )
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update tenant"
        )
    return tenant
