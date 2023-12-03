from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from time import sleep
import asyncio
from http import HTTPStatus
from typing import Dict, List
from uuid import UUID, uuid4
from fastapi import FastAPI
from pydantic import BaseModel, Field
import init

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



async def long_task(queue: asyncio.Queue, pitch: UploadFile = File(...)):
   # await asyncio.sleep(1)  # simulate 
   
    queue.put(init.analyse_video('./../luc65r'))
    with open('./../luc65r', 'wb') as out_file:
      out_file.write( pitch.file.read()) 
    await queue.put(None)


async def start_new_task(uid: UUID, pitch: UploadFile = File(...)) -> None:

    queue = asyncio.Queue()
    task = asyncio.create_task(long_task(queue, pitch))

    while progress := await queue.get():  # monitor task progress
        jobs[uid].progress = progress

    jobs[uid].status = "complete"
    jobs[uid].result = {
        "global": {
            "Ancrage du corps": "2",
            "Gestes": "1",
            "Texte - débit/fréquence": "1",
            "Texte - variété": "2",
            "Voix - dynamisme": "1",
            "Voix - prononciation": "1",
            "Voix - débit": "2",
            "Calme (vs anxiété)": "2",
            "Emotions": "1",
            "Note globale": "1"
        },
        "events": {
            "0": {
                "timestamp": 2.770384,
                "type": "(S)ourire",
                "note": "good"
            },
            "1": {
                "timestamp": 6.581967,
                "type": "(G)estes",
                "note": "ok"
            },
            "2": {
                "timestamp": 6.860036,
                "type": "(F)iller",
                "note": "bad"
            },
            "3": {
                "timestamp": 10.043611,
                "type": "(F)iller",
                "note": "bad"
            },
            "4": {
                "timestamp": 12.264452,
                "type": "(G)estes",
                "note": "bad"
            },
            "5": {
                "timestamp": 20.4936,
                "type": "(G)estes",
                "note": "good"
            },
            "6": {
                "timestamp": 23.894982,
                "type": "(G)estes",
                "note": "bad"
            },
            "7": {
                "timestamp": 25.668381,
                "type": "(M)ouvements du corps",
                "note": "bad"
            },
            "8": {
                "timestamp": 27.895432,
                "type": "(F)iller",
                "note": "bad"
            },
            "9": {
                "timestamp": 30.074568,
                "type": "(G)estes",
                "note": "bad"
            },
            "10": {
                "timestamp": 33.453615,
                "type": "(M)ouvements du corps",
                "note": "bad"
            },
            "11": {
                "timestamp": 39.166679,
                "type": "(G)estes",
                "note": "good"
            },
            "12": {
                "timestamp": 43.592089,
                "type": "(G)estes",
                "note": "good"
            },
            "13": {
                "timestamp": 45.127512,
                "type": "(S)ourire",
                "note": "bad"
            },
            "14": {
                "timestamp": 49.920537,
                "type": "(F)iller",
                "note": "bad"
            },
            "15": {
                "timestamp": 50.935829,
                "type": "(G)estes",
                "note": "bad"
            },
            "16": {
                "timestamp": 55.027347,
                "type": "(G)estes",
                "note": "bad"
            },
            "17": {
                "timestamp": 56.659114,
                "type": "(S)ourire",
                "note": "bad"
            },
            "18": {
                "timestamp": 66.294991,
                "type": "(F)iller",
                "note": "bad"
            },
            "19": {
                "timestamp": 72.00329,
                "type": "(F)iller",
                "note": "bad"
            },
            "20": {
                "timestamp": 75.552202,
                "type": "(G)estes",
                "note": "bad"
            },
            "21": {
                "timestamp": 77.654373,
                "type": "(F)iller",
                "note": "bad"
            },
            "22": {
                "timestamp": 78.354304,
                "type": "(G)estes",
                "note": "bad"
            },
            "23": {
                "timestamp": 79.420687,
                "type": "(F)iller",
                "note": "bad"
            },
            "24": {
                "timestamp": 81.428397,
                "type": "(F)iller",
                "note": "bad"
            },
            "25": {
                "timestamp": 85.080738,
                "type": "(F)iller",
                "note": "bad"
            },
            "26": {
                "timestamp": 86.195394,
                "type": "(S)ourire",
                "note": "bad"
            },
            "27": {
                "timestamp": 86.195394,
                "type": "(S)ourire",
                "note": "bad"
            },
            "28": {
                "timestamp": 86.195394,
                "type": "(S)ourire",
                "note": "bad"
            },
            "29": {
                "timestamp": 87.936561,
                "type": "(F)iller",
                "note": "bad"
            }
        }
    }


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

		
    