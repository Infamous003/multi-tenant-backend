from datetime import datetime, timezone
from sqlmodel import Session, select
from sqlalchemy.exc import SQLAlchemyError
from app.core.logging import get_logger
from app.db.models.tenants import Tenant
from app.domain.exceptions import TenantNotFound
from app.domain.exceptions import QuotaExceeded

class UsageService:
    def __init__(self, db: Session):
        self.db = db
        self.logger = get_logger(__name__)

    @staticmethod
    def get_current_month_period() -> tuple[datetime, datetime]:
        """
        Calculate the start(inclusive) and end(exclusive) datetime for the current month (UTC).

        Returns:
            tuple[datetime, datetime]: Start and end datetime of the current month.
        """        

        now = datetime.now(timezone.utc)

        period_start = datetime(
            year=now.year,
            month=now.month,
            day=1,
            tzinfo=timezone.utc,
        )

        if now.month == 12:
            period_end = datetime(
                year=now.year + 1,
                month=1,
                day=1,
                tzinfo=timezone.utc,
            )
        else:
            period_end = datetime(
                year=now.year,
                month=now.month + 1,
                day=1,
                tzinfo=timezone.utc,
            )

        return period_start, period_end
    
    def reset_monthly_usage(self, tenant_id: int) -> Tenant:
        """
        Reset a tenant's current usage to zero.

        Args:
            tenant_id (int): ID of the tenant to reset.
        
        Returns:
            Tenant: Tenant object after reset.
        
        Raises:
            TenantNotFound: If the tenant does not exist.
            SQLAlchemyError: If database operation fails.
        """

        self.logger.info(f"Resetting monthly usage tenant_id={tenant_id}")
        now = datetime.now(timezone.utc)

        try:
            query = (
                select(Tenant)
                .where(Tenant.id == tenant_id)
                .with_for_update()
            )
            tenant = self.db.exec(query).first()
            
            if not tenant:
                raise TenantNotFound()
            
            tenant.current_usage = 0
            tenant.updated_at = now

            self.db.commit()
            self.db.refresh(tenant)

            self.logger.info(f"Reset tenant usage tenant_id={tenant_id}")
            return tenant
        except SQLAlchemyError:
            self.logger.exception(f"Failed to reset monthly usage tenant_id={tenant_id}")
            raise
    
    def get_tenant_usage(self, tenant_id: int) -> Tenant:
        """
        Retrieve a tenant by ID.
        
        Args:
            tenant_id (int): ID of the tenant to retrieve.
        
        Returns:
            Tenant: Tenant object.
        
        Raises:
            TenantNotFound: If the tenant does not exist
        """

        self.logger.info(f"Retrieving tenant usage tenant_id={tenant_id}")

        tenant = self.db.get(Tenant, tenant_id)

        if not tenant:
            self.logger.warning(f"Tenant not found tenant_id={tenant_id}")
            raise TenantNotFound()

        self.logger.info(f"Retrieved tenant usage tenant_id={tenant_id}")
        return tenant
    
    def increment_tenant_usage(self, tenant_id: int, amount: int) -> Tenant:
        """
        Increment a tenant's current usage by the given amount(>=1).

        If the current time is past the tenant's period_end, the usage is reset to 0
        and period_start and period_end are recalculated for the new calender month.

        Args:
            tenant_id (int): ID of the tenant to increment usage for.
            amount (int): Amount to increment the usage by.
        
        Returns:
            Tenant: Tenant object after increment.
        
        Raises:
            TenantNotFound: If the tenant does not exist.
            QuotaExceeded: If increment exceeds the tenant's monthly usage limit.
            SQLAlchemyError: if database operation fails.
        """

        self.logger.info(f"Incrementing tenant usage tenant_id={tenant_id} amount={amount}")

        now = datetime.now(timezone.utc)

        try:
            query = (
                select(Tenant)
                .where(Tenant.id == tenant_id)
                .with_for_update()
            )

            tenant = self.db.exec(query).first()

            if not tenant:
                raise TenantNotFound()

            if now >= tenant.period_end:
                self.logger.info(f"New month detected, resetting usage tenant_id={tenant_id}")
                period_start, period_end = self.get_current_month_period()
                tenant.current_usage = 0
                tenant.period_start = period_start
                tenant.period_end = period_end

            if tenant.current_usage + amount > tenant.monthly_usage_limit:
                raise QuotaExceeded()

            tenant.current_usage += amount
            tenant.updated_at = now

            self.db.commit()
            self.db.refresh(tenant)

            self.logger.info(f"Incremented tenant usage tenant_id={tenant_id} current_usage={tenant.current_usage}")
            return tenant
        except SQLAlchemyError:
            self.db.rollback()
            self.logger.exception(f"Failed to increment tenant usage tenant_id={tenant_id}")
            raise