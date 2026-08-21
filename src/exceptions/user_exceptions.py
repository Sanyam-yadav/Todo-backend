class UserException(Exception):
    """Base exception for user operations"""
    pass

class UserAlreadyExistsError(UserException):
    """Raised when a user with the given email already exists"""
    def __init__(self, email: str):
        self.detail = f"User with email {email} already exists"
        super().__init__(self.detail)

class InvalidCredentialsError(UserException):
    """Raised when authentication fails due to invalid credentials"""
    def __init__(self, message: str = "Invalid credentials"):
        self.detail = message
        super().__init__(self.detail)

class UserNotFoundError(UserException):
    """Raised when a user is not found"""
    def __init__(self, user_identifier: str):
        self.detail = f"User '{user_identifier}' not found"
        super().__init__(self.detail)