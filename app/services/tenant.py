from sqlmodel import Session
from sqlalchemy.exc import SQLAlchemyError
from app.db.models.tenants import Tenant
from app.db.models.api_key import APIKey
from app.schemas.tenants import TenantCreate
from app.core.security import generate_api_key, hash_api_key
from app.core.logging import get_logger
from app.services.usage import UsageService


class TenantService:
    def __init__(self, db: Session):
        self.db = db
        self.logger = get_logger(__name__)

    def create_tenant(self, payload: TenantCreate) -> tuple[Tenant, str]:
        """
        Create a new tenant in the DB and generate a corresponding API key.

        Args:
            payload (TenantCreate): Data for the new tenant.

        Returns:
            tuple[Tenant, str]: The created Tenant object and its plain API key.
        
        Raises:
            SQLAlchemyError: If database operation fails.
        """

        self.logger.info(
            "Creating tenant", 
            plan=payload.plan_name,
        )

        period_start, period_end = UsageService.get_current_month_period()

        new_tenant = Tenant(
            plan_name=payload.plan_name,
            monthly_usage_limit=payload.monthly_usage_limit,
            current_usage=0,
            period_start=period_start,
            period_end=period_end,
        )

        plain_api_key = generate_api_key()
        hashed_api_key = hash_api_key(plain_api_key) # TODO: will use this when api_keys table is added

        try:
            self.db.add(new_tenant)
            self.db.flush()

            api_key_obj = APIKey(
                tenant_id=new_tenant.id,
                api_key_hash=hashed_api_key,
            )
            self.db.add(api_key_obj)
            self.db.commit()
            self.db.refresh(new_tenant)

            self.logger.info(
                "Tenant created successfully in DB",
                tenant_id=new_tenant.id,
            )

            return new_tenant, plain_api_key
        except SQLAlchemyError:
            self.db.rollback()
            self.logger.exception("Failed to create tenant")
            raise