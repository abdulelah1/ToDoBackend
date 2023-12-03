from fastapi import FastAPI, Depends
from app.routers import auth, tasks, sharing
from app.routers.tasks import get_all_tasks

app = FastAPI()


app.include_router(auth.router, prefix='/auth', tags=['auth'])
app.include_router(tasks.router, prefix="/tasks", tags=['tasks'])
app.include_router(sharing.router, prefix="/share", tags=['share'])
