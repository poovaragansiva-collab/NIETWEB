/* ── Timetable JS ──────────────────────────────────── */
let currentTimetableId = null;
let currentTimetableData = null;

async function generateTimetable() {
  const btn = document.getElementById('gen-btn');
  const dept     = document.getElementById('gen-dept').value;
  const semester = parseInt(document.getElementById('gen-sem').value);
  const section  = document.getElementById('gen-section').value.trim() || 'A';
  const daysCount= parseInt(document.getElementById('gen-days').value);
  const slots    = parseInt(document.getElementById('gen-slots').value);
  const year     = document.getElementById('gen-year').value.trim() || '2024-25';

  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Generating…';

  try {
    const result = await api.post('/timetable/generate', {
      department: dept,
      semester,
      section,
      academic_year: year,
      working_days_count: daysCount,
      slots_per_day: slots,
    });
    currentTimetableId = result.id;
    currentTimetableData = result;
    renderTimetable(result);
    document.getElementById('export-btn').disabled = false;
    ui.toast('Timetable generated successfully!', 'success');
  } catch (e) {
    ui.toast(e.message, 'error');
  } finally {
    btn.disabled = false;
    btn.innerHTML = '⚡ Generate Timetable';
  }
}

function renderTimetable(data) {
  const display = document.getElementById('timetable-display');
  const table   = document.getElementById('timetable-table');
  const days    = data.working_days || Object.keys(data.schedule);
  const slots   = data.slots_per_day;

  // Header info
  document.getElementById('tt-meta').textContent =
    `${data.department} · Semester ${data.semester} · Section ${data.section} · ${data.academic_year}`;

  // Build table
  let html = '<thead><tr><th></th>';
  for (let s = 1; s <= slots; s++) {
    html += `<th>Slot ${s}<br><span style="font-size:10px;font-weight:400;color:var(--text-muted)">Period ${s}</span></th>`;
  }
  html += '</tr></thead><tbody>';

  days.forEach((day, di) => {
    html += `<tr><td class="day-label">${day}</td>`;
    for (let s = 1; s <= slots; s++) {
      const cell = (data.schedule[day] || {})[String(s)];
      if (!cell || cell.type === 'free') {
        html += `<td class="tt-cell type-free"><span style="font-size:18px;opacity:0.3">—</span></td>`;
      } else {
        const delay = (di * slots + s) * 0.035;
        html += `
          <td class="tt-cell type-${cell.type}" style="animation-delay:${delay}s"
              title="${cell.staff_name || 'No staff'}">
            <div class="cell-code">${cell.subject_code || ''}</div>
            <div class="cell-name">${cell.subject_name || ''}</div>
            ${cell.staff_name ? `<div class="cell-staff">👤 ${cell.staff_name}</div>` : ''}
          </td>`;
      }
    }
    html += '</tr>';
  });
  html += '</tbody>';

  table.innerHTML = html;
  display.style.display = 'block';
  display.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

async function exportPDF() {
  if (!currentTimetableId) return;
  window.open(`http://localhost:8000/api/export/timetable/${currentTimetableId}/pdf`, '_blank');
}

async function loadExistingTimetable() {
  const dept    = document.getElementById('view-dept').value;
  const sem     = document.getElementById('view-sem').value;
  const section = document.getElementById('view-section').value.trim() || 'A';

  try {
    const result = await api.get(`/timetable/${dept}/${sem}/${section}`);
    currentTimetableId = result.id;
    currentTimetableData = result;
    renderTimetable(result);
    document.getElementById('export-btn').disabled = false;
    ui.toast('Timetable loaded', 'success');
  } catch (e) {
    ui.toast(e.message, 'error');
  }
}

document.addEventListener('DOMContentLoaded', () => {
  // nothing to autoload
});
