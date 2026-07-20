from uuid import UUID

from app.core.celery_app import celery_app
from app.db.base import SessionLocal
from app.db.models.user import User  # noqa: F401 - needed to register the User mapper for the Task.user relationship
from app.db.models.task import Task, TaskStatus
from app.agents.graph import workflow_graph


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

        initial_state = {
            "original_request": task.input_text,
            "research_output": "",
            "summary_output": "",
            "email_output": "",
        }

        final_state = workflow_graph.invoke(initial_state)

        task.plan = ["research", "summary", "email"]
        task.steps_output = {
            "research": final_state["research_output"],
            "summary": final_state["summary_output"],
            "email": final_state["email_output"],
        }
        task.final_result = final_state["email_output"]
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