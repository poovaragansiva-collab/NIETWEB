from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional
from bson import ObjectId
from datetime import datetime

from ..database import subject_collection
from ..schemas.subject import SubjectCreate, SubjectUpdate

router = APIRouter()


def serialize_subject(doc) -> dict:
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc


@router.get("/", response_model=List[dict])
async def list_subjects(
    dept: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    semester: Optional[int] = Query(None),
):
    query = {}
    if dept:
        query["department"] = dept
    if type:
        query["type"] = type
    if semester:
        query["semester"] = semester

    subjects = []
    async for doc in subject_collection.find(query):
        subjects.append(serialize_subject(doc))
    return subjects


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_subject(data: SubjectCreate):
    existing = await subject_collection.find_one({"code": data.code})
    if existing:
        raise HTTPException(status_code=400, detail="Subject code already exists")

    doc = data.model_dump()
    doc["created_at"] = datetime.utcnow()
    result = await subject_collection.insert_one(doc)
    created = await subject_collection.find_one({"_id": result.inserted_id})
    return serialize_subject(created)


@router.get("/{subject_id}", response_model=dict)
async def get_subject(subject_id: str):
    try:
        doc = await subject_collection.find_one({"_id": ObjectId(subject_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID")
    if not doc:
        raise HTTPException(status_code=404, detail="Subject not found")
    return serialize_subject(doc)


@router.put("/{subject_id}", response_model=dict)
async def update_subject(subject_id: str, data: SubjectUpdate):
    try:
        oid = ObjectId(subject_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID")

    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")

    result = await subject_collection.update_one({"_id": oid}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Subject not found")

    doc = await subject_collection.find_one({"_id": oid})
    return serialize_subject(doc)


@router.delete("/{subject_id}")
async def delete_subject(subject_id: str):
    try:
        oid = ObjectId(subject_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID")

    result = await subject_collection.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Subject not found")
    return {"message": "Subject deleted successfully"}
