from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from uuid import UUID
from ..database.core import get_db
from ..services.todo_service import TodoService
from ..services.schemas import TodoCreate, TodoUpdate, TodoResponse
from ..dependencies.auth import get_current_user
from ..exceptions.todo_exceptions import (
    TodoNotFoundError,
    TodoCreationError,
    TodoUpdateError,
    TodoDeletionError,
)

router = APIRouter(prefix="/todos", tags=["todos"])


def get_todo_service(db: Session = Depends(get_db)) -> TodoService:
    return TodoService(db)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=TodoResponse)
def create_todo(
    todo_data: TodoCreate,
    service: TodoService = Depends(get_todo_service),
    current_user: UUID = Depends(get_current_user),
):
    return service.create_todo(
        user_id=current_user,
        title=todo_data.title,
        description=todo_data.description,
        priority=todo_data.priority,
    )


@router.get("/", response_model=list[TodoResponse])
def get_all_todos(
    service: TodoService = Depends(get_todo_service),
    current_user: UUID = Depends(get_current_user),
):
    return service.get_all_todos(current_user)


@router.get("/{todo_id}", response_model=TodoResponse)
def get_todo_by_id(
    todo_id: UUID,
    service: TodoService = Depends(get_todo_service),
    current_user: UUID = Depends(get_current_user),
):
    return service.get_todo_by_id(current_user, todo_id)  # ✅ FIXED


@router.put("/{todo_id}", response_model=TodoResponse)
def update_todo(
    todo_id: UUID,
    todo_data: TodoUpdate,
    service: TodoService = Depends(get_todo_service),
    current_user: UUID = Depends(get_current_user),
):
    return service.update_todo(
        current_user, todo_id, **todo_data.model_dump(exclude_unset=True)
    )


@router.put("/{todo_id}/complete", response_model=TodoResponse)
def complete_todo(
    todo_id: UUID,
    service: TodoService = Depends(get_todo_service),
    current_user: UUID = Depends(get_current_user),
):
    return service.complete_todo(current_user, todo_id)  # ✅ FIXED


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(
    todo_id: UUID,
    service: TodoService = Depends(get_todo_service),
    current_user: UUID = Depends(get_current_user),
):
    service.delete_todo(current_user, todo_id)  # ✅ FIXED
