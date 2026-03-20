from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings

client = AsyncIOMotorClient(settings.mongodb_uri)
db = client[settings.db_name]

# Collections
staff_collection = db["staff"]
subject_collection = db["subjects"]
classroom_collection = db["classrooms"]
timetable_collection = db["timetables"]
attendance_collection = db["attendance"]
