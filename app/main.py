"""
Main FastAPI application module.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException

from .schemas import TodoTaskModel
from app.users.router import router as users_router
from app.orders.router import router as orders_router
from app.payments.router import router as payments_router
from app.analytics.router import router as analytics_router


app = FastAPI(
    title="FastAPI Harness Sample",
    description="A test-rich FastAPI playground for advanced testing scenarios",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users_router)
app.include_router(orders_router)
app.include_router(payments_router)
app.include_router(analytics_router)

all_tasks: dict = {}


@app.post("/task", response_model=TodoTaskModel)
def create_task(task: TodoTaskModel):
    task_slug = task.slug

    if all_tasks.get(task_slug) is not None:
        raise HTTPException(
            detail={'message': 'Task with this slug already exists :('}, 
            status_code=400
        )

    # Ideally this should be persisted in some db
    all_tasks[task_slug] = task
    
    return task


@app.delete("/task/{task_slug}")
def remove_task(task_slug: str):
    if all_tasks.get(task_slug) is None:
        raise HTTPException(
            detail={'message': 'No task with the specified slug found :('}, 
            status_code=404
        )

    all_tasks.pop(task_slug)


@app.get("/tasks")
def tasks():
    tasks = [
        task for task in all_tasks.values()
    ]

    return tasks


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to FastAPI Harness Sample",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}