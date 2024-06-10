import asyncio
import logging
import time
from datetime import datetime
from threading import Thread

import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from rich import print
from rich.logging import RichHandler

LEVEL = logging.INFO

formatter = logging.Formatter("%(asctime)s - %(message)s", datefmt="[%X]")
logger = logging.getLogger(__name__)
sh = RichHandler()
sh.setFormatter(formatter)
sh.setLevel(LEVEL)
logger.addHandler(sh)
logger.setLevel(LEVEL)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


sio = socketio.AsyncServer(cors_allowed_origins="*", async_mode="asgi", logger=False)
sio_app = socketio.ASGIApp(sio, other_asgi_app=app)

cid = None


async def send_message():
    global cid

    print("thread start")
    await asyncio.sleep(1)

    while True:
        if cid is None:
            break

        await sio.emit(
            "notify",
            {"data": f"{datetime.now()}", "msg": "api -> client"},
            to=cid,
        )
        await asyncio.sleep(1)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@sio.on("connect")
async def connect(sid, environ):
    global cid
    cid = sid
    logging.info("Client connected: ", sid)

    # asyncio.create_task(send_message())


@sio.event
async def disconnect(sid):
    global cid
    cid = None

    logging.info("Client disconnected: ", sid)


@sio.on("msg")
async def receive_message(sid, data):
    logging.info(f"Message from client: {data}")
    await sio.emit("response", {"data": "Message received by FastAPI"}, to=sid)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(sio_app, host="localhost", port=9090)
