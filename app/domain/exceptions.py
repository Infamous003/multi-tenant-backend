class TenantNotFound(Exception):
    """
    Raised when a tenant is not found in the database.
    """
    pass

class QuotaExceeded(Exception):
    """
    Raised when a tenant has exceeded their usage quota.
    """
    pass