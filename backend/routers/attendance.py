from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional
from bson import ObjectId
from datetime import datetime

from ..database import attendance_collection
from ..schemas.attendance import AttendanceCreate

router = APIRouter()


def serialize_attendance(doc) -> dict:
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    if "marked_at" in doc and doc["marked_at"]:
        doc["marked_at"] = doc["marked_at"].isoformat()
    present = len(doc.get("present_students", []))
    total = doc.get("total_students", 1)
    doc["percentage"] = round((present / total) * 100, 2) if total > 0 else 0.0
    return doc


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def mark_attendance(data: AttendanceCreate):
    # Prevent duplicate entry for same date/section/subject/slot
    existing = await attendance_collection.find_one(
        {
            "date": data.date,
            "department": data.department,
            "semester": data.semester,
            "section": data.section,
            "subject_code": data.subject_code,
            "slot": data.slot,
        }
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Attendance already marked for this slot. Use update to modify.",
        )

    doc = data.model_dump()
    doc["marked_at"] = datetime.utcnow()
    result = await attendance_collection.insert_one(doc)
    created = await attendance_collection.find_one({"_id": result.inserted_id})
    return serialize_attendance(created)


@router.get("/report", response_model=List[dict])
async def get_report(
    dept: str = Query(...),
    sem: int = Query(...),
    section: str = Query(...),
    from_date: Optional[str] = Query(None, alias="from"),
    to_date: Optional[str] = Query(None, alias="to"),
):
    query: dict = {"department": dept, "semester": sem, "section": section}
    if from_date or to_date:
        date_filter = {}
        if from_date:
            date_filter["$gte"] = from_date
        if to_date:
            date_filter["$lte"] = to_date
        query["date"] = date_filter

    records = []
    async for doc in attendance_collection.find(query).sort("date", -1):
        records.append(serialize_attendance(doc))
    return records


@router.get("/student/{usn}", response_model=List[dict])
async def get_student_attendance(usn: str):
    records = []
    async for doc in attendance_collection.find({"present_students": usn}):
        records.append(serialize_attendance(doc))
    return records


@router.get("/subject/{subject_code}/percentage")
async def get_subject_percentage(subject_code: str):
    total_classes = await attendance_collection.count_documents(
        {"subject_code": subject_code}
    )
    if total_classes == 0:
        return {"subject_code": subject_code, "total_classes": 0, "average_percentage": 0}

    pipeline = [
        {"$match": {"subject_code": subject_code}},
        {
            "$project": {
                "percentage": {
                    "$multiply": [
                        {"$divide": [{"$size": "$present_students"}, "$total_students"]},
                        100,
                    ]
                }
            }
        },
        {"$group": {"_id": None, "avg": {"$avg": "$percentage"}}},
    ]

    result = []
    async for doc in attendance_collection.aggregate(pipeline):
        result.append(doc)

    avg = round(result[0]["avg"], 2) if result else 0
    return {
        "subject_code": subject_code,
        "total_classes": total_classes,
        "average_percentage": avg,
    }


@router.get("/", response_model=List[dict])
async def list_attendance(
    dept: Optional[str] = Query(None),
    sem: Optional[int] = Query(None),
    section: Optional[str] = Query(None),
    date: Optional[str] = Query(None),
):
    query = {}
    if dept:
        query["department"] = dept
    if sem:
        query["semester"] = sem
    if section:
        query["section"] = section
    if date:
        query["date"] = date

    records = []
    async for doc in attendance_collection.find(query).sort("date", -1).limit(100):
        records.append(serialize_attendance(doc))
    return records
