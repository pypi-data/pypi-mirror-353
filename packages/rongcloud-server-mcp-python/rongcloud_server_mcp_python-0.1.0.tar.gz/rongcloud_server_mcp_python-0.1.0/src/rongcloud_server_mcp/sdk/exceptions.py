from dataclasses import dataclass


@dataclass
class APIErrorDetail:
    """Detailed information about a RongCloud API error.
    Used only in RongCloudAPIError.
    """

    code: int
    message: str
    http_status: int = 200


class RongCloudError(Exception):
    """Base exception for RongCloud-related errors."""

    def __init__(self, message: str):
        super().__init__(message)


class RongCloudAPIError(RongCloudError):
    """Exception raised when a RongCloud API call fails with a valid response."""

    def __init__(self, error_detail: APIErrorDetail):
        self.error_detail = error_detail
        message = f'HTTP {error_detail.http_status} - [{error_detail.code}] {error_detail.message}'
        super().__init__(message)


class RongCloudRequestError(RongCloudError):
    """Exception raised for request-level errors (e.g., network issues)."""

    def __init__(self, message: str = 'Request failed'):
        super().__init__(message)


class RongCloudValidationError(RongCloudError):
    """Exception raised for input validation failures."""

    def __init__(self, message: str = 'Validation failed'):
        super().__init__(message)
