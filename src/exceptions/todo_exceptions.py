class TodoException(Exception):
    """Base exception for todo operations"""
    pass

class TodoNotFoundError(TodoException):
    """Raised when todo is not found"""
    def __init__(self, todo_id: str):
        self.detail = f"Todo with id {todo_id} not found"
        super().__init__(self.detail)

class TodoCreationError(TodoException):
    """Raised when todo creation fails"""
    def __init__(self, message: str = "Failed to create todo"):
        self.detail = message
        super().__init__(self.detail)

class TodoUpdateError(TodoException):
    """Raised when todo update fails"""
    def __init__(self, todo_id: str):
        self.detail = f"Failed to update todo with id {todo_id}"
        super().__init__(self.detail)

class TodoDeletionError(TodoException):
    """Raised when todo deletion fails"""
    def __init__(self, todo_id: str):
        self.detail = f"Failed to delete todo with id {todo_id}"
        super().__init__(self.detail)