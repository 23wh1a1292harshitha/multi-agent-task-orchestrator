from fastapi import FastAPI

from app.api.routes import auth, tasks

app = FastAPI(title="Multi-Agent Task Orchestrator")

app.include_router(auth.router)
app.include_router(tasks.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}