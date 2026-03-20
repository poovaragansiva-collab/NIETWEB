# 🎓 College Timetable & Attendance Management System

A full-stack academic management system with a production-grade dark-theme dashboard.

**Tech Stack:** FastAPI + Motor (MongoDB Atlas) · Vanilla HTML/CSS/JS  
**Design:** Deep navy + indigo accent · Playfair Display + DM Sans · Glass-morphism cards

---

## 📁 Project Structure

```
college_tms/
├── backend/
│   ├── main.py                    ← FastAPI app entry point
│   ├── config.py                  ← Pydantic settings (reads .env)
│   ├── database.py                ← Motor async MongoDB client + collections
│   ├── models/                    ← (reserved for ODM models if needed)
│   ├── schemas/
│   │   ├── staff.py               ← Pydantic schemas: StaffCreate, StaffResponse
│   │   ├── subject.py
│   │   ├── classroom.py
│   │   ├── timetable.py
│   │   └── attendance.py
│   ├── routers/
│   │   ├── staff.py               ← GET/POST/PUT/DELETE /api/staff
│   │   ├── subjects.py            ← GET/POST/PUT/DELETE /api/subjects
│   │   ├── classrooms.py          ← GET/POST/PUT/DELETE /api/classrooms
│   │   ├── timetable.py           ← POST /api/timetable/generate + CRUD
│   │   ├── attendance.py          ← POST /api/attendance + reports
│   │   └── export.py              ← GET /api/export/timetable/{id}/pdf
│   ├── services/
│   │   ├── timetable_engine.py    ← Core lab-first allocation algorithm
│   │   └── pdf_service.py         ← WeasyPrint PDF generation
│   ├── templates/
│   │   └── timetable_pdf.html     ← Jinja2 PDF template
│   └── static/
│       └── college_logo.png       ← Placeholder logo (replace with yours)
├── frontend/
│   ├── index.html                 ← Dashboard with live stats
│   ├── staff.html                 ← Staff CRUD + availability grid
│   ├── subjects.html              ← Subject CRUD + color picker
│   ├── classrooms.html            ← Classroom cards + facilities
│   ├── timetable.html             ← Generate + view timetable grid
│   ├── attendance.html            ← Mark + report attendance
│   ├── css/
│   │   ├── main.css               ← Design system, tokens, components
│   │   ├── sidebar.css            ← Sidebar, header, layout
│   │   ├── timetable.css          ← Timetable grid cells, legend
│   │   └── animations.css         ← Keyframes, stagger, spinner
│   └── js/
│       ├── api.js                 ← fetch-based API client
│       ├── ui.js                  ← Toast, modal, skeleton, sidebar
│       ├── staff.js               ← Staff page logic
│       ├── timetable.js           ← Timetable generate + render
│       └── attendance.js          ← Attendance mark + report
├── requirements.txt
├── .env                           ← Configure your MongoDB URI here
└── README.md
```

---

## ⚡ Quick Start

### 1. Prerequisites

- Python 3.10+
- MongoDB Atlas account (free tier works) **or** local MongoDB
- A modern browser

### 2. Clone & Install

```bash
cd college_tms
python -m venv venv

# Activate:
source venv/bin/activate          # macOS/Linux
# OR
venv\Scripts\activate             # Windows

pip install -r requirements.txt
```

### 3. Configure MongoDB

Edit `.env`:

```env
# MongoDB Atlas (replace with your connection string)
MONGODB_URI=mongodb+srv://<user>:<pass>@cluster0.xxxxx.mongodb.net/college_tms?retryWrites=true&w=majority

# OR local MongoDB
# MONGODB_URI=mongodb://localhost:27017

DB_NAME=college_tms
COLLEGE_NAME=ABC Engineering College
COLLEGE_LOGO_PATH=backend/static/college_logo.png
```

### 4. Start the Backend

```bash
# From the college_tms/ directory:
uvicorn backend.main:app --reload --port 8000
```

Visit **http://localhost:8000/docs** for interactive Swagger UI.

### 5. Serve the Frontend

```bash
# Option A — Python simple server:
cd frontend && python -m http.server 3000

# Option B — VS Code Live Server extension (recommended)
# Right-click index.html → Open with Live Server

# Option C — Node http-server:
npx http-server frontend -p 3000
```

Visit **http://localhost:3000**

---

## 🔄 Recommended Setup Workflow

1. **Add Staff** (`/staff.html`) — Create faculty profiles with availability slots
2. **Add Subjects** (`/subjects.html`) — Define theory + lab subjects with staff assignments
3. **Add Classrooms** (`/classrooms.html`) — Register rooms and labs
4. **Generate Timetable** (`/timetable.html`) — Select dept/sem/section → click Generate
5. **Mark Attendance** (`/attendance.html`) — Record per-slot attendance, view reports

---

## 🗂️ API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/staff` | List all staff |
| POST | `/api/staff` | Create staff |
| PUT | `/api/staff/{id}` | Update staff |
| DELETE | `/api/staff/{id}` | Delete staff |
| GET | `/api/subjects?dept=CSE&type=lab` | List subjects (filterable) |
| POST | `/api/subjects` | Create subject |
| GET | `/api/classrooms` | List classrooms |
| POST | `/api/classrooms` | Create classroom |
| **POST** | **`/api/timetable/generate`** | **🔑 Generate timetable** |
| GET | `/api/timetable/{dept}/{sem}/{section}` | Get timetable |
| PUT | `/api/timetable/{id}/slot` | Override a slot |
| POST | `/api/attendance` | Mark attendance |
| GET | `/api/attendance/report?dept=CSE&sem=3&section=A` | Get report |
| GET | `/api/export/timetable/{id}/pdf` | Download PDF |

Full docs at: `http://localhost:8000/docs`

---

## 🧠 Timetable Engine Algorithm

The engine in `backend/services/timetable_engine.py` uses a two-phase greedy allocation:

**Phase 1 — Labs first** (most constrained):
- Finds consecutive slot pairs (e.g. slots 3–4) per day
- Checks staff is free for both slots before assigning
- Books both slots as a single lab block

**Phase 2 — Theory subjects** (sorted by hours/week descending):
- Most-hours-first ensures heavily taught subjects get placed before easier ones
- Per subject, iterates days × slots to find the next free + staff-available slot
- Assigns and marks the slot in `staff_schedule` to prevent double-booking

**Conflict detection:**
- `staff_schedule[staff_id][day]` tracks occupied slots per staff per day
- `_is_staff_free()` checks before every assignment
- Free periods are inserted automatically for unfilled slots

---

## 🎨 Design System

| Token | Value | Usage |
|-------|-------|-------|
| `--bg-primary` | `#0A0F1E` | Page background |
| `--bg-surface` | `#111827` | Cards, panels |
| `--accent-primary` | `#6366F1` | Buttons, active nav, borders |
| `--accent-secondary` | `#F59E0B` | Lab cells, warnings |
| `--accent-success` | `#10B981` | Success states |
| `--accent-danger` | `#EF4444` | Delete, errors |
| Display font | Playfair Display | Page titles, card headings |
| Body font | DM Sans | All UI text |

---

## 🔧 Customisation

**Add a new department:**
Update the `<select>` dropdowns in `staff.html`, `subjects.html`, `classrooms.html`, `timetable.html`, and `attendance.html`.

**Change working hours:**
Edit `TimetableEngine.DAYS_MAP` in `backend/services/timetable_engine.py`.

**Use WeasyPrint PDF:**
WeasyPrint requires GTK libraries. On Ubuntu: `sudo apt install libpangocairo-1.0-0`. On macOS: `brew install pango`. If not available, the export falls back to HTML download.

**Replace logo:**
Drop your PNG at `backend/static/college_logo.png` (128×128 px recommended).

---

## 📦 MongoDB Collections & Indexes

| Collection | Unique Indexes |
|------------|----------------|
| `staff` | `email` |
| `subjects` | `code` |
| `classrooms` | `room_number` |
| `timetables` | `(department, semester, section)` |
| `attendance` | `(date, dept, sem, section, subject_code, slot)` |

Indexes are created automatically on startup via the `lifespan` handler in `main.py`.

---

## 🚀 Production Notes

- Set `CORS allow_origins` to your specific frontend domain in `backend/main.py`
- Use environment variables for all secrets (never commit `.env`)
- Consider adding JWT authentication for the admin routes
- MongoDB Atlas free tier (M0) is sufficient for ~100 staff, 500 subjects, 10,000 attendance records

---

*Built with FastAPI · Motor · MongoDB Atlas · Vanilla JS*
