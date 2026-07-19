from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, Any

from app.db.models.task import TaskStatus


class TaskCreate(BaseModel):
    input_text: str


class TaskOut(BaseModel):
    id: UUID
    status: TaskStatus
    input_text: str
    plan: Optional[Any] = None
    steps_output: Optional[Any] = None
    final_result: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True