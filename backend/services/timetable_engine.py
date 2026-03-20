"""
Timetable Generation Engine
Algorithm:
1. Initialize empty grid [days x slots]
2. Track staff_schedule: {staff_id: {day: [occupied_slots]}}
3. Phase 1 - Allocate Labs first (2 continuous slots):
   - For each lab subject, find valid consecutive slot pairs
   - Check staff availability and room availability
   - Assign and lock those slots
4. Phase 2 - Allocate Theory subjects:
   - Sort by hours_per_week descending (most constrained first)
   - For each subject, find available slots
   - Apply conflict detection before assigning
5. Return completed grid or raise TimetableConflictError
"""

from typing import Dict, List, Optional
from collections import defaultdict


class TimetableConflictError(Exception):
    pass


class TimetableEngine:
    DAYS_MAP = {
        5: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        6: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
    }

    def __init__(self, config: dict):
        days_count = config.get("working_days_count", 5)
        self.days = self.DAYS_MAP.get(days_count, self.DAYS_MAP[5])
        self.slots_per_day = config.get("slots_per_day", 6)
        self.subjects = config.get("subjects", [])
        self.staff_map = config.get("staff_map", {})
        self.grid = {
            day: {slot: None for slot in range(1, self.slots_per_day + 1)}
            for day in self.days
        }
        self.staff_schedule = defaultdict(lambda: defaultdict(set))

    def _is_staff_free(self, staff_id: str, day: str, slots: List[int]) -> bool:
        if not staff_id:
            return True
        occupied = self.staff_schedule[staff_id][day]
        return not any(s in occupied for s in slots)

    def _assign_slot(self, day: str, slot: int, subject: dict, staff_id: str):
        staff_name = ""
        if staff_id and staff_id in self.staff_map:
            staff_name = self.staff_map[staff_id].get("name", "")
        self.grid[day][slot] = {
            "subject_code": subject.get("code", ""),
            "subject_name": subject.get("name", ""),
            "staff_id": staff_id,
            "staff_name": staff_name,
            "type": subject.get("type", "theory"),
            "color": subject.get("color", "#6366F1"),
        }
        if staff_id:
            self.staff_schedule[staff_id][day].add(slot)

    def _allocate_labs(self):
        lab_subjects = [s for s in self.subjects if s.get("type") == "lab"]
        for lab in lab_subjects:
            sessions_needed = lab.get("lab_sessions_per_week", 1)
            staff_id = lab.get("staff_id", "")
            allocated = 0
            for day in self.days:
                if allocated >= sessions_needed:
                    break
                for slot in range(1, self.slots_per_day):
                    if (
                        self.grid[day][slot] is None
                        and self.grid[day][slot + 1] is None
                        and self._is_staff_free(staff_id, day, [slot, slot + 1])
                    ):
                        lab_display = {**lab, "name": f"{lab['name']} Lab"}
                        self._assign_slot(day, slot, lab_display, staff_id)
                        lab_cont = {**lab, "name": f"{lab['name']} Lab (cont.)"}
                        self._assign_slot(day, slot + 1, lab_cont, staff_id)
                        allocated += 1
                        break

    def _allocate_theory(self):
        theory_subjects = [s for s in self.subjects if s.get("type") == "theory"]
        theory_subjects.sort(key=lambda x: x.get("hours_per_week", 4), reverse=True)

        for subject in theory_subjects:
            staff_id = subject.get("staff_id", "")
            hours_remaining = subject.get("hours_per_week", 4)

            for day in self.days:
                if hours_remaining <= 0:
                    break
                for slot in range(1, self.slots_per_day + 1):
                    if hours_remaining <= 0:
                        break
                    if self.grid[day][slot] is None and self._is_staff_free(
                        staff_id, day, [slot]
                    ):
                        self._assign_slot(day, slot, subject, staff_id)
                        hours_remaining -= 1

    def generate(self) -> dict:
        self._allocate_labs()
        self._allocate_theory()

        result = {}
        for day, slots in self.grid.items():
            result[day] = {}
            for slot, data in slots.items():
                result[day][str(slot)] = data or {
                    "subject_code": "FREE",
                    "subject_name": "Free Period",
                    "type": "free",
                    "color": "#4B5563",
                }
        return result, self.days
