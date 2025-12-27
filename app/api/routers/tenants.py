from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.api.deps import require_admin_api_key
from app.db.db import get_db
from app.schemas.tenants import TenantCreate, TenantCreateResponse
from app.services.tenant import TenantService

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