from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from .database import (
    staff_collection,
    subject_collection,
    classroom_collection,
    timetable_collection,
    attendance_collection,
)
from .routers import staff, subjects, classrooms, timetable, attendance, export


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create indexes on startup
    await staff_collection.create_index("email", unique=True)
    await subject_collection.create_index("code", unique=True)
    await classroom_collection.create_index("room_number", unique=True)
    await timetable_collection.create_index(
        [("department", 1), ("semester", 1), ("section", 1)]
    )
    await attendance_collection.create_index(
        [("date", 1), ("department", 1), ("semester", 1), ("section", 1), ("subject_code", 1), ("slot", 1)],
        unique=True,
    )
    yield


app = FastAPI(
    title="College TMS API",
    version="1.0.0",
    description="College Timetable and Attendance Management System",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.include_router(staff.router, prefix="/api/staff", tags=["Staff"])
app.include_router(subjects.router, prefix="/api/subjects", tags=["Subjects"])
app.include_router(classrooms.router, prefix="/api/classrooms", tags=["Classrooms"])
app.include_router(timetable.router, prefix="/api/timetable", tags=["Timetable"])
app.include_router(attendance.router, prefix="/api/attendance", tags=["Attendance"])
app.include_router(export.router, prefix="/api/export", tags=["Export"])


@app.get("/")
async def root():
    return {"message": "College TMS API v1.0", "docs": "/docs", "status": "running"}
