from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime


class TimetableGenerateRequest(BaseModel):
    department: str
    semester: int
    section: str = "A"
    academic_year: str = "2024-25"
    working_days_count: int = 5
    slots_per_day: int = 6


class SlotOverride(BaseModel):
    day: str
    slot: int
    subject_code: str
    subject_name: str
    staff_id: str
    staff_name: str
    type: str = "theory"


class TimetableResponse(BaseModel):
    id: str
    department: str
    semester: int
    section: str
    academic_year: str
    working_days: List[str]
    slots_per_day: int
    schedule: Dict[str, Any]
    generated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
