from fastapi import APIRouter, HTTPException, status
from typing import List
from bson import ObjectId
from datetime import datetime

from ..database import classroom_collection
from ..schemas.classroom import ClassroomCreate, ClassroomUpdate

router = APIRouter()


def serialize_classroom(doc) -> dict:
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc


@router.get("/", response_model=List[dict])
async def list_classrooms():
    classrooms = []
    async for doc in classroom_collection.find():
        classrooms.append(serialize_classroom(doc))
    return classrooms


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_classroom(data: ClassroomCreate):
    existing = await classroom_collection.find_one({"room_number": data.room_number})
    if existing:
        raise HTTPException(status_code=400, detail="Room number already exists")

    doc = data.model_dump()
    doc["created_at"] = datetime.utcnow()
    result = await classroom_collection.insert_one(doc)
    created = await classroom_collection.find_one({"_id": result.inserted_id})
    return serialize_classroom(created)


@router.get("/{classroom_id}", response_model=dict)
async def get_classroom(classroom_id: str):
    try:
        doc = await classroom_collection.find_one({"_id": ObjectId(classroom_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID")
    if not doc:
        raise HTTPException(status_code=404, detail="Classroom not found")
    return serialize_classroom(doc)


@router.put("/{classroom_id}", response_model=dict)
async def update_classroom(classroom_id: str, data: ClassroomUpdate):
    try:
        oid = ObjectId(classroom_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID")

    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")

    result = await classroom_collection.update_one({"_id": oid}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Classroom not found")

    doc = await classroom_collection.find_one({"_id": oid})
    return serialize_classroom(doc)


@router.delete("/{classroom_id}")
async def delete_classroom(classroom_id: str):
    try:
        oid = ObjectId(classroom_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID")

    result = await classroom_collection.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Classroom not found")
    return {"message": "Classroom deleted successfully"}
