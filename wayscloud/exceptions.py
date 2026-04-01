class WaysCloudError(Exception):
    """Base exception for all WAYSCloud API errors."""

    def __init__(self, message: str, status_code: int = 0, detail: str = ""):
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(message)


class AuthenticationError(WaysCloudError):
    """401/403 -- invalid or missing credentials."""
    pass


class NotFoundError(WaysCloudError):
    """404 -- resource not found."""
    pass


class ValidationError(WaysCloudError):
    """422 -- request validation failed."""
    pass


class ServerError(WaysCloudError):
    """5xx -- server-side error."""
    pass
