class SabiaAuthError(Exception):
    """Base exception for Sabiá authentication errors."""


class SabiaTokenError(SabiaAuthError):
    """Raised when token exchange fails."""


class SabiaUserInfoError(SabiaAuthError):
    """Raised when fetching user info fails."""


class SabiaAPIError(SabiaAuthError):
    """Raised when the Sabiá user management API returns an error."""

    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.status_code = status_code


class SabiaStateMismatchError(SabiaAuthError):
    """Raised when the OAuth2 state parameter does not match (CSRF protection)."""
