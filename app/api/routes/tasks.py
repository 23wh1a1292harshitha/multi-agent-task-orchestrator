from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import get_db, get_current_user
from app.db.models.user import User
from app.schemas.task import TaskCreate, TaskOut
from app.services import task_service
from app.main import limiter

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def submit_task(
    request: Request,
    task_in: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = task_service.create_task(db, current_user, task_in)
    return task