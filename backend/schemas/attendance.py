from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime


class AttendanceCreate(BaseModel):
    date: str
    department: str
    semester: int
    section: str
    subject_code: str
    staff_id: str
    slot: int
    present_students: List[str] = []
    total_students: int = 60


class AttendanceResponse(BaseModel):
    id: str
    date: str
    department: str
    semester: int
    section: str
    subject_code: str
    staff_id: str
    slot: int
    present_students: List[str]
    total_students: int
    percentage: Optional[float] = None
    marked_at: Optional[datetime] = None

    class Config:
        from_attributes = True
