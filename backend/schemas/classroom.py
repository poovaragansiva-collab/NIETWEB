from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ClassroomBase(BaseModel):
    room_number: str
    building: str
    capacity: int = 60
    type: str = "theory"  # theory | lab
    department: str = ""
    facilities: list = []


class ClassroomCreate(ClassroomBase):
    pass


class ClassroomUpdate(BaseModel):
    room_number: Optional[str] = None
    building: Optional[str] = None
    capacity: Optional[int] = None
    type: Optional[str] = None
    department: Optional[str] = None
    facilities: Optional[list] = None


class ClassroomResponse(ClassroomBase):
    id: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
