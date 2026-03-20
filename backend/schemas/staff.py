from pydantic import BaseModel, EmailStr, Field
from typing import Dict, List, Optional
from datetime import datetime


class StaffBase(BaseModel):
    name: str
    department: str
    email: str
    subjects: List[str] = []
    availability: Dict[str, List[int]] = {}


class StaffCreate(StaffBase):
    pass


class StaffUpdate(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    email: Optional[str] = None
    subjects: Optional[List[str]] = None
    availability: Optional[Dict[str, List[int]]] = None


class StaffResponse(StaffBase):
    id: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
