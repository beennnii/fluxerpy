"""
Exception classes for Fluxer.py
"""


class FluxerException(Exception):
    """Base exception for Fluxer.py"""
    pass


class AuthenticationError(FluxerException):
    """Raised when authentication fails"""
    def __init__(self, message, response_body=None):
        super().__init__(message)
        self.response_body = response_body


class NotFoundError(FluxerException):
    """Raised when a resource is not found"""
    pass


class RateLimitError(FluxerException):
    """Raised when rate limit is exceeded"""
    def __init__(self, message, retry_after=None):
        super().__init__(message)
        self.retry_after = retry_after


class APIError(FluxerException):
    """Raised when the API returns an error"""
    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.status_code = status_code
