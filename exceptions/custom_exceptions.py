class AppError(Exception):
    """Base class for application exceptions"""
    def __init__(self, message, code=500):
        super().__init__(message)
        self.message = message
        self.code = code

class AuthenticationError(AppError):
    def __init__(self, message="Authentication failed"):
        super().__init__(message, 401)

class AuthorizationError(AppError):
    def __init__(self, message="Permission denied"):
        super().__init__(message, 403)

class PermissionDeniedError(AuthorizationError):
    """Raised when user lacks specific permission"""
    def __init__(self, role, permission):
        super().__init__(f"Role '{role}' missing permission: '{permission}'")

class InvalidCredentialsError(AuthenticationError):
    def __init__(self, message="Invalid email or password"):
        super().__init__(message)

class DuplicateEntryError(AppError):
    def __init__(self, resource):
        super().__init__(f"{resource} already exists", 409)

class StackUnderflowError(Exception):
    """Raised when accessing empty stack"""
    def __init__(self, message="Stack is empty"):
        super().__init__(message)

class QueueUnderflowError(Exception):
    """Raised when accessing empty queue"""
    def __init__(self, message="Queue is empty"):
        super().__init__(message)

class LinkedListEmptyError(Exception):
    """Raised when operation invalid on empty list"""
    def __init__(self, message="LinkedList is empty"):
        super().__init__(message)

class AttendanceAlreadyMarkedError(AppError):
    def __init__(self, message="Attendance already marked for this lecture"):
        super().__init__(message, 409)

class LectureNotActiveError(AppError):
    def __init__(self):
        super().__init__("Lecture is not active", 400)

class UniversityInactiveError(AppError):
    def __init__(self):
        super().__init__("University subscription is inactive", 403)

class ValidationError(AppError):
    def __init__(self, message):
        super().__init__(message, 400)

class DatabaseError(AppError):
    """Raised when a database operation fails"""
    def __init__(self, message="Database operation failed"):
        super().__init__(message, 500)

class RecordNotFoundError(AppError):
    """Raised when a specific record is not found in the database"""
    def __init__(self, message="Record not found"):
        super().__init__(message, 404)

class DuplicateRecordError(AppError):
    """Raised when a duplicate record insertion is attempted"""
    def __init__(self, message="Duplicate record exists"):
        super().__init__(message, 409)

class SessionNotFoundError(AppError):
    """Raised when a session is not found or invalid"""
    def __init__(self):
        super().__init__("Session is invalid or expired", 401)

class LectureAlreadyActiveError(AppError):
    def __init__(self, message="A lecture is already active"):
        super().__init__(message, 409)
