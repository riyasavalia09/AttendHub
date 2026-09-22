class AuthenticationError(Exception):
    """Base authentication error"""
    def __init__(self, message="Authentication failed"):
        self.message = message
        super().__init__(self.message)


class InvalidCredentialsError(AuthenticationError):
    """Raised when credentials are invalid"""
    def __init__(self, message="Invalid email or password"):
        super().__init__(message)


class AuthorizationError(Exception):
    """Raised when user lacks permission"""
    def __init__(self, message="Insufficient permissions"):
        self.message = message
        super().__init__(self.message)


class AccountInactiveError(AuthenticationError):
    """Raised when account is inactive"""
    def __init__(self, message="Account is inactive"):
        super().__init__(message)


class UniversityInactiveError(AuthenticationError):
    """Raised when university is inactive"""
    def __init__(self, message="University is inactive"):
        super().__init__(message)


class DuplicateAccountError(Exception):
    """Raised when account already exists"""
    def __init__(self, message="Account already exists"):
        self.message = message
        super().__init__(self.message)


class ValidationError(Exception):
    """Raised when input validation fails"""
    def __init__(self, message="Validation failed"):
        self.message = message
        super().__init__(self.message)


class SessionNotFoundError(Exception):
    """Raised when session is not found"""
    def __init__(self, message="Session not found"):
        self.message = message
        super().__init__(self.message)
