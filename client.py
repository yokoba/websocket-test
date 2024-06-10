import logging

import socketio
from rich.logging import RichHandler

LEVEL = logging.INFO

formatter = logging.Formatter("%(asctime)s - %(message)s", datefmt="[%X]")
logger = logging.getLogger(__name__)
sh = RichHandler()
sh.setFormatter(formatter)
sh.setLevel(LEVEL)
logger.addHandler(sh)
logger.setLevel(LEVEL)


sio = socketio.Client()


@sio.on("connect")
def connect():
    logging.info("Connected from client to server")


@sio.event
def disconnect():
    logging.info("Disconnected from server")


@sio.on("response", namespace="/")
def response(data):
    logger.info(f"Response from server: {data}")


@sio.on("notify", namespace="/")
def receive_message(data):
    logger.info(f"Notify Message from server: {data}")


def main():
    try:
        logger.info("Connect to server")
        sio.connect("http://localhost:9090")
        logger.info("Connected to server")

        logger.info("Send message from client to server")
        sio.emit("msg", {"data": "Hello from Python client"})
        sio.wait()
    except Exception as e:
        print("sio connect exception")
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
