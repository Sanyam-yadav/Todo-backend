import os

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from .database.core import engine, Base
from .entities.todo import Todo
from .entities.user import User

from .controller.todo_controller import router as todo_router
from .controller.auth_controller import router as auth_router

from .exceptions.todo_exceptions import (
    TodoNotFoundError,
    TodoCreationError,
    TodoUpdateError,
    TodoDeletionError,
)

from .exceptions.user_exceptions import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
    UserNotFoundError,
)

# Create database tables
Base.metadata.create_all(bind=engine)


# Create FastAPI application
app = FastAPI(title="Todo App", version="1.0.0")


# ============================================================
# CORS CONFIGURATION
# ============================================================

ALLOWED_ORIGINS = [
    # Local development
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "https://localhost:5173",
    # Production React frontend on Vercel
    "https://todo-frontend-git-main-sanyamy97-6516s-projects.vercel.app",
]


# Optional: Add frontend URL from Render environment variable
frontend_url = os.getenv("FRONTEND_URL")

if frontend_url:
    # Remove trailing slash if someone accidentally adds one
    frontend_url = frontend_url.rstrip("/")

    if frontend_url not in ALLOWED_ORIGINS:
        ALLOWED_ORIGINS.append(frontend_url)


app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# HEALTH CHECK
# ============================================================


@app.get("/health")
async def health_check():
    return {"status": "ok"}


# ============================================================
# TODO EXCEPTION HANDLERS
# ============================================================


@app.exception_handler(TodoNotFoundError)
async def todo_not_found_handler(request, exc: TodoNotFoundError):
    return JSONResponse(status_code=404, content={"detail": exc.detail})


@app.exception_handler(TodoCreationError)
async def todo_creation_error_handler(request, exc: TodoCreationError):
    return JSONResponse(status_code=400, content={"detail": exc.detail})


@app.exception_handler(TodoUpdateError)
async def todo_update_error_handler(request, exc: TodoUpdateError):
    return JSONResponse(status_code=400, content={"detail": exc.detail})


@app.exception_handler(TodoDeletionError)
async def todo_deletion_error_handler(request, exc: TodoDeletionError):
    return JSONResponse(status_code=400, content={"detail": exc.detail})


# ============================================================
# USER EXCEPTION HANDLERS
# ============================================================


@app.exception_handler(UserAlreadyExistsError)
async def user_already_exists_handler(request, exc: UserAlreadyExistsError):
    return JSONResponse(status_code=409, content={"detail": exc.detail})


@app.exception_handler(InvalidCredentialsError)
async def invalid_credentials_handler(request, exc: InvalidCredentialsError):
    return JSONResponse(status_code=401, content={"detail": exc.detail})


@app.exception_handler(UserNotFoundError)
async def user_not_found_handler(request, exc: UserNotFoundError):
    return JSONResponse(status_code=404, content={"detail": exc.detail})


# ============================================================
# REGISTER ROUTERS
# ============================================================

app.include_router(todo_router)
app.include_router(auth_router)
