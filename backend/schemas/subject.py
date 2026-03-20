from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SubjectBase(BaseModel):
    code: str
    name: str
    department: str
    hours_per_week: int = 4
    type: str = "theory"  # theory | lab
    staff_id: Optional[str] = None
    semester: int = 1
    color: str = "#6366F1"


class SubjectCreate(SubjectBase):
    pass


class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    hours_per_week: Optional[int] = None
    type: Optional[str] = None
    staff_id: Optional[str] = None
    semester: Optional[int] = None
    color: Optional[str] = None


class SubjectResponse(SubjectBase):
    id: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
