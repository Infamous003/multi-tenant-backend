from datetime import datetime, timezone
from sqlmodel import Session
from app.core.logging import get_logger

class UsageService:
    def __init__(self, db_session: Session):
        self.db_session = db_session
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