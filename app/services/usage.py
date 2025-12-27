from datetime import datetime, timezone
from sqlmodel import Session, select
from sqlalchemy.exc import SQLAlchemyError
from app.core.logging import get_logger
from app.db.models.tenants import Tenant
from app.domain.exceptions import TenantNotFound

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

        self.logger.info("Resetting monthly usage", tenant_id=tenant_id)
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

            self.logger.info("Reset tenant usage", extra={"tenant_id": tenant_id})
            return tenant
        except SQLAlchemyError:
            self.logger.exception("Failed to reset monthly usage", tenant_id=tenant_id)
            raise
    
    