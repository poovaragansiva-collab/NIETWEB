from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from bson import ObjectId

from ..database import timetable_collection, attendance_collection
from ..services.pdf_service import generate_timetable_pdf

router = APIRouter()


@router.get("/timetable/{timetable_id}/pdf")
async def export_timetable_pdf(timetable_id: str):
    try:
        oid = ObjectId(timetable_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID")

    doc = await timetable_collection.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Timetable not found")

    doc["id"] = str(doc["_id"])
    del doc["_id"]
    if "generated_at" in doc and doc["generated_at"]:
        doc["generated_at"] = doc["generated_at"].strftime("%d %b %Y, %H:%M")

    pdf_bytes = generate_timetable_pdf(doc)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=timetable_{doc['department']}_S{doc['semester']}{doc['section']}.pdf"
        },
    )


@router.get("/attendance/{dept}/{sem}/pdf")
async def export_attendance_pdf(dept: str, sem: int, section: str = "A"):
    records = []
    async for doc in attendance_collection.find(
        {"department": dept, "semester": sem, "section": section}
    ).sort("date", -1):
        doc["id"] = str(doc["_id"])
        del doc["_id"]
        present = len(doc.get("present_students", []))
        total = doc.get("total_students", 1)
        doc["percentage"] = round((present / total) * 100, 2) if total > 0 else 0.0
        records.append(doc)

    if not records:
        raise HTTPException(status_code=404, detail="No attendance records found")

    # Simple HTML report
    rows = "".join(
        f"<tr><td>{r['date']}</td><td>{r['subject_code']}</td><td>{r['slot']}</td>"
        f"<td>{len(r['present_students'])}/{r['total_students']}</td><td>{r['percentage']}%</td></tr>"
        for r in records
    )
    html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8">
    <style>body{{font-family:Arial,sans-serif;padding:20px}}
    h1{{color:#6366F1}}table{{width:100%;border-collapse:collapse}}
    th{{background:#6366F1;color:white;padding:8px}}td{{border:1px solid #ddd;padding:8px}}</style>
    </head><body>
    <h1>Attendance Report — {dept} Sem {sem} Sec {section}</h1>
    <table><thead><tr><th>Date</th><th>Subject</th><th>Slot</th><th>Present/Total</th><th>%</th></tr></thead>
    <tbody>{rows}</tbody></table></body></html>"""

    return Response(
        content=html.encode(),
        media_type="text/html",
        headers={"Content-Disposition": f"attachment; filename=attendance_{dept}_S{sem}.html"},
    )
