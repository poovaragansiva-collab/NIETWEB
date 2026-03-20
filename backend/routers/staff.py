from fastapi import APIRouter, HTTPException, status
from typing import List
from bson import ObjectId
from datetime import datetime

from ..database import staff_collection, subject_collection
from ..schemas.staff import StaffCreate, StaffUpdate, StaffResponse

router = APIRouter()


def serialize_staff(doc) -> dict:
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc


@router.get("/", response_model=List[dict])
async def list_staff():
    staff = []
    async for doc in staff_collection.find():
        staff.append(serialize_staff(doc))
    return staff


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_staff(data: StaffCreate):
    # Check email uniqueness
    existing = await staff_collection.find_one({"email": data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    doc = data.model_dump()
    doc["created_at"] = datetime.utcnow()
    result = await staff_collection.insert_one(doc)
    created = await staff_collection.find_one({"_id": result.inserted_id})
    return serialize_staff(created)


@router.get("/{staff_id}", response_model=dict)
async def get_staff(staff_id: str):
    try:
        doc = await staff_collection.find_one({"_id": ObjectId(staff_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID")
    if not doc:
        raise HTTPException(status_code=404, detail="Staff not found")
    return serialize_staff(doc)


@router.put("/{staff_id}", response_model=dict)
async def update_staff(staff_id: str, data: StaffUpdate):
    try:
        oid = ObjectId(staff_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID")

    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")

    result = await staff_collection.update_one({"_id": oid}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Staff not found")

    doc = await staff_collection.find_one({"_id": oid})
    return serialize_staff(doc)


@router.delete("/{staff_id}")
async def delete_staff(staff_id: str):
    try:
        oid = ObjectId(staff_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID")

    result = await staff_collection.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Staff not found")
    return {"message": "Staff deleted successfully"}


@router.get("/{staff_id}/subjects")
async def get_staff_subjects(staff_id: str):
    try:
        staff = await staff_collection.find_one({"_id": ObjectId(staff_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID")
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")

    subject_codes = staff.get("subjects", [])
    subjects = []
    async for doc in subject_collection.find({"code": {"$in": subject_codes}}):
        doc["id"] = str(doc["_id"])
        del doc["_id"]
        subjects.append(doc)
    return subjects
