from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from time import sleep
import asyncio
from http import HTTPStatus
from typing import Dict, List
from uuid import UUID, uuid4
from fastapi import FastAPI
from pydantic import BaseModel, Field
import analyze
from threading import Thread

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Job(BaseModel):
    uid: UUID = Field(default_factory=uuid4)
    status: str = "in_progress"
    progress: int = 0
    result: int = None

jobs: Dict[UUID, Job] = {}  # Dict as job storage

def long_task(uid: UUID):
    result = analyze.analyze(f"../{uid}")
    jobs[uid].status = "complete"
    jobs[uid].result = result
    

async def start_new_task(uid: UUID, pitch: UploadFile = File(...)) -> None:
    with open(f"../{uid}", "wb") as out_file:
        out_file.write(pitch.file.read())

    thread = Thread(target = long_task, args = (uid,))
    thread.start()

@app.post("/new_task", status_code=HTTPStatus.ACCEPTED)
async def task_handler(
    background_tasks: BackgroundTasks, 
    pitch: UploadFile = File(...)
):
    new_task = Job()
    jobs[new_task.uid] = new_task
    background_tasks.add_task(start_new_task, new_task.uid, pitch)
    return new_task


@app.get("/task/{uid}")
async def status_handler(uid: UUID):
    return jobs[uid]

		
    
