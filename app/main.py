import logging
import os
import socket
import sys
from contextlib import asynccontextmanager

import psycopg
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger("task-api")

APP_VERSION=os.getenv("APP_VERSION", "1.0")
HOSTNAME=socket.gethostname()

REQUIRED_ENV = ["DB_HOST", "DB_USER", "DB_PASSWORD"]
missing = [name for name in REQUIRED_ENV if not os.getenv(name)]

if missing:
    log.error("FATAL: missing required environment variables: %s", ", ".join(missing))
    sys.exit(1)


DB_HOST = os.environ["DB_HOST"]
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "tasks")
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]


state={"healthy":True}


def connect():
    return psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        connect_timeout=3,
    )