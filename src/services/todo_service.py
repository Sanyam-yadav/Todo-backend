from sqlalchemy.orm import Session
from ..entities.todo import Todo  # ✅ CORRECT (relative import)
import uuid  # Keep uuid import
from src.exceptions.todo_exceptions import (
    TodoNotFoundError,
    TodoCreationError,
    TodoUpdateError,
    TodoDeletionError,
)


class TodoService:
    def __init__(self, db: Session):
        self.db = db

    def create_todo(
        self,
        user_id: uuid.UUID,
        title: str,
        description: str = "",
        priority: str = "medium",
    ) -> Todo:
        try:
            todo = Todo(
                id=uuid.uuid4(),
                user_id=user_id,
                title=title,
                description=description,
                priority=priority,
            )
            self.db.add(todo)
            self.db.commit()
            self.db.refresh(todo)
            return todo
        except Exception:
            raise TodoCreationError()

    def get_all_todos(self, user_id: uuid.UUID) -> list[Todo]:
        return self.db.query(Todo).filter(Todo.user_id == user_id).all()

    def get_todo_by_id(self, user_id: uuid.UUID, todo_id: uuid.UUID) -> Todo:
        todo = (
            self.db.query(Todo)
            .filter(Todo.id == todo_id, Todo.user_id == user_id)
            .first()
        )
        if not todo:
            raise TodoNotFoundError(str(todo_id))
        return todo

    def update_todo(self, user_id: uuid.UUID, todo_id: uuid.UUID, **kwargs) -> Todo:
        try:
            todo = self.get_todo_by_id(user_id, todo_id)
            for key, value in kwargs.items():
                if value is not None:
                    setattr(todo, key, value)
            self.db.commit()
            self.db.refresh(todo)
            return todo
        except TodoNotFoundError:
            raise
        except Exception:
            self.db.rollback()
            raise TodoUpdateError(str(todo_id))

    def complete_todo(self, user_id: uuid.UUID, todo_id: uuid.UUID) -> Todo:
        todo = self.get_todo_by_id(user_id, todo_id)
        todo.completed = True
        self.db.commit()
        self.db.refresh(todo)
        return todo

    def delete_todo(self, user_id: uuid.UUID, todo_id: uuid.UUID) -> bool:
        try:
            todo = self.get_todo_by_id(user_id, todo_id)
            self.db.delete(todo)
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            raise TodoDeletionError(str(todo_id))
