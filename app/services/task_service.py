from sqlalchemy.orm import Session
from uuid import UUID

from app.db.models.task import Task, TaskStatus
from app.db.models.user import User
from app.schemas.task import TaskCreate
from app.workers.tasks import run_task_workflow


def create_task(db: Session, user: User, task_in: TaskCreate) -> Task:
    task = Task(
        user_id=user.id,
        input_text=task_in.input_text,
        status=TaskStatus.PENDING,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    run_task_workflow.delay(str(task.id))

    return task


def get_task(db: Session, user: User, task_id: UUID) -> Task | None:
    return (
        db.query(Task)
        .filter(Task.id == task_id, Task.user_id == user.id)
        .first()
    )


def list_tasks(db: Session, user: User) -> list[Task]:
    return (
        db.query(Task)
        .filter(Task.user_id == user.id)
        .order_by(Task.created_at.desc())
        .all()
    )