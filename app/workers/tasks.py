from uuid import UUID

from app.core.celery_app import celery_app
from app.db.base import SessionLocal
from app.db.models.user import User  # noqa: F401 - needed to register the User mapper for the Task.user relationship
from app.db.models.task import Task, TaskStatus


@celery_app.task(name="run_task_workflow")
def run_task_workflow(task_id: str):
    db = SessionLocal()
    task = None
    try:
        task = db.query(Task).filter(Task.id == UUID(task_id)).first()
        if task is None:
            return

        task.status = TaskStatus.RUNNING
        db.commit()

        # --- placeholder for now, real agent logic comes in Step 7 ---
        task.final_result = f"Placeholder result for: {task.input_text}"
        task.status = TaskStatus.COMPLETED
        db.commit()

    except Exception as e:
        if task is not None:
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            db.commit()
        raise

    finally:
        db.close()