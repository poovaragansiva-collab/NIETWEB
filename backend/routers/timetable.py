from fastapi import APIRouter, HTTPException, status
from typing import List
from bson import ObjectId
from datetime import datetime

from ..database import timetable_collection, subject_collection, staff_collection
from ..schemas.timetable import TimetableGenerateRequest, SlotOverride
from ..services.timetable_engine import TimetableEngine

router = APIRouter()


def serialize_timetable(doc) -> dict:
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    if "generated_at" in doc and doc["generated_at"]:
        doc["generated_at"] = doc["generated_at"].isoformat()
    return doc


@router.post("/generate", response_model=dict, status_code=status.HTTP_201_CREATED)
async def generate_timetable(req: TimetableGenerateRequest):
    # Fetch subjects for this dept/semester
    subjects = []
    async for doc in subject_collection.find(
        {"department": req.department, "semester": req.semester}
    ):
        doc["id"] = str(doc["_id"])
        del doc["_id"]
        subjects.append(doc)

    if not subjects:
        raise HTTPException(
            status_code=400,
            detail=f"No subjects found for {req.department} semester {req.semester}. Add subjects first.",
        )

    # Build staff map
    staff_map = {}
    async for doc in staff_collection.find():
        staff_map[str(doc["_id"])] = {"name": doc.get("name", ""), "department": doc.get("department", "")}

    # Map staff_id field in subjects
    for sub in subjects:
        if "staff_id" in sub and sub["staff_id"]:
            sub["staff_id"] = str(sub["staff_id"])

    config = {
        "working_days_count": req.working_days_count,
        "slots_per_day": req.slots_per_day,
        "subjects": subjects,
        "staff_map": staff_map,
    }

    engine = TimetableEngine(config)
    schedule, working_days = engine.generate()

    timetable_doc = {
        "department": req.department,
        "semester": req.semester,
        "section": req.section,
        "academic_year": req.academic_year,
        "working_days": working_days,
        "slots_per_day": req.slots_per_day,
        "schedule": schedule,
        "generated_at": datetime.utcnow(),
    }

    result = await timetable_collection.insert_one(timetable_doc)
    created = await timetable_collection.find_one({"_id": result.inserted_id})
    return serialize_timetable(created)


@router.get("/", response_model=List[dict])
async def list_timetables():
    timetables = []
    async for doc in timetable_collection.find():
        timetables.append(serialize_timetable(doc))
    return timetables


@router.get("/staff/{staff_id}", response_model=dict)
async def get_staff_timetable(staff_id: str):
    """Return all slots across all timetables where this staff teaches."""
    result = {"staff_id": staff_id, "schedule": {}}
    async for tt in timetable_collection.find():
        for day, slots in tt.get("schedule", {}).items():
            for slot_num, cell in slots.items():
                if cell and str(cell.get("staff_id", "")) == staff_id:
                    key = f"{tt['department']}_S{tt['semester']}{tt['section']}"
                    if key not in result["schedule"]:
                        result["schedule"][key] = {}
                    if day not in result["schedule"][key]:
                        result["schedule"][key][day] = {}
                    result["schedule"][key][day][slot_num] = cell
    return result


@router.get("/{dept}/{sem}/{section}", response_model=dict)
async def get_timetable(dept: str, sem: int, section: str):
    doc = await timetable_collection.find_one(
        {"department": dept, "semester": sem, "section": section}
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Timetable not found")
    return serialize_timetable(doc)


@router.put("/{timetable_id}/slot", response_model=dict)
async def override_slot(timetable_id: str, override: SlotOverride):
    try:
        oid = ObjectId(timetable_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID")

    update_key = f"schedule.{override.day}.{override.slot}"
    slot_data = {
        "subject_code": override.subject_code,
        "subject_name": override.subject_name,
        "staff_id": override.staff_id,
        "staff_name": override.staff_name,
        "type": override.type,
    }

    result = await timetable_collection.update_one(
        {"_id": oid}, {"$set": {update_key: slot_data}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Timetable not found")

    doc = await timetable_collection.find_one({"_id": oid})
    return serialize_timetable(doc)


@router.delete("/{timetable_id}")
async def delete_timetable(timetable_id: str):
    try:
        oid = ObjectId(timetable_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID")

    result = await timetable_collection.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Timetable not found")
    return {"message": "Timetable deleted successfully"}
