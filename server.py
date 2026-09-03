#!/usr/bin/env python
# coding: utf-8

# ## Running the Server
# 
# During development
# ```bash
# python server.py
# ```
# This enables reload=True, so the server restarts automatically when you edit the code.
# 
# For production (recommended)
# ```bash
# uvicorn server:app --host 0.0.0.0 --port 8000 --workers 4
# ```
# Replace 4 with the number of CPU cores on your server if appropriate.

# In[ ]:


from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

import uvicorn
import socket
import sqlite3

from utils import dbms_controller as db


# ==========================================================
# Database
# ==========================================================

conn = sqlite3.connect(
    "utils/attendance.db",
    check_same_thread=False
)


# ==========================================================
# Daily Function
# ==========================================================

def daily_task():
    db.initialize_attendance(conn)


# ==========================================================
# Scheduler
# ==========================================================

scheduler = BackgroundScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):

    # Run every day at 00:00
    scheduler.add_job(
        daily_task,
        CronTrigger(hour=00, minute=00),
        id="daily_task",
        replace_existing=True
    )

    scheduler.start()

    print("Daily scheduler started.")

    yield

    scheduler.shutdown()

    print("Daily scheduler stopped.")


# ==========================================================
# FastAPI
# ==========================================================

app = FastAPI(
    title="Attendance API",
    version="1.0",
    lifespan=lifespan
)


# ==========================================================
# Request Model
# ==========================================================

class AttendanceRequest(BaseModel):
    name: str
    user_id: int
    secret_code: str
    device_id: str


# ==========================================================
# Response Model
# ==========================================================

class AttendanceResponse(BaseModel):
    success: bool
    message: str


# ==========================================================
# PLACEHOLDER FUNCTIONS
# ==========================================================

def verify_device(device_id: str) -> bool:
    return db.device_exists(conn, device_id)


def verify_user_exists(user_id: int, name: str, code: str) -> bool:
    return db.user_exists(conn, user_id, name, code)


def verify_secret_code(user_id: int, secret_code: str) -> bool:
    return db.verify_user_hash(conn, secret_code)


def mark_attendance(user_id: int, device_id: str) -> bool:
    return db.mark_presence(conn, user_id, device_id)


# ==========================================================
# API Endpoint
# ==========================================================

@app.post("/attendance", response_model=AttendanceResponse)
async def attendance(data: AttendanceRequest):

    if not verify_device(data.device_id):
        return AttendanceResponse(
            success=False,
            message="Invalid Device"
        )

    if not verify_user_exists(data.user_id, data.name, data.secret_code):
        return AttendanceResponse(
            success=False,
            message="User Not Found"
        )

    if not verify_secret_code(data.user_id, data.secret_code):
        return AttendanceResponse(
            success=False,
            message="Invalid Security Code"
        )

    if not mark_attendance(data.user_id, data.device_id):
        return AttendanceResponse(
            success=False,
            message="Attendance Failed"
        )

    return AttendanceResponse(
        success=True,
        message=f"Attendance Marked Successfully for {data.user_id}"
    )


# ==========================================================
# Health Check
# ==========================================================

@app.get("/")
async def home():
    return {
        "status": "online",
        "message": "Attendance Server Running"
    }


# ==========================================================
# Run Server
# ==========================================================

if __name__ == "__main__":

    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)

    print(f"Server running at: http://{ip}:8000")

    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

