/* ── Attendance JS ──────────────────────────────────── */

async function markAttendance() {
  const date        = document.getElementById('att-date').value;
  const dept        = document.getElementById('att-dept').value;
  const semester    = parseInt(document.getElementById('att-sem').value);
  const section     = document.getElementById('att-section').value.trim() || 'A';
  const subjectCode = document.getElementById('att-subject').value.trim().toUpperCase();
  const staffId     = document.getElementById('att-staff').value.trim();
  const slot        = parseInt(document.getElementById('att-slot').value);
  const totalStr    = document.getElementById('att-total').value.trim();
  const presentStr  = document.getElementById('att-present').value.trim();

  if (!date || !subjectCode || !slot) {
    ui.toast('Please fill in all required fields', 'error');
    return;
  }

  const total    = parseInt(totalStr) || 60;
  const present  = presentStr.split(',').map(s => s.trim()).filter(Boolean);

  const btn = document.getElementById('mark-btn');
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Marking…';

  try {
    await api.post('/attendance', {
      date,
      department: dept,
      semester,
      section,
      subject_code: subjectCode,
      staff_id: staffId || 'unknown',
      slot,
      present_students: present,
      total_students: total,
    });
    ui.toast('Attendance marked successfully!', 'success');
    await loadReport();
  } catch (e) {
    ui.toast(e.message, 'error');
  } finally {
    btn.disabled = false;
    btn.innerHTML = '✅ Mark Attendance';
  }
}

async function loadReport() {
  const dept    = document.getElementById('rep-dept').value;
  const sem     = document.getElementById('rep-sem').value;
  const section = document.getElementById('rep-section').value.trim() || 'A';
  const from    = document.getElementById('rep-from').value;
  const to      = document.getElementById('rep-to').value;

  let path = `/attendance/report?dept=${dept}&sem=${sem}&section=${section}`;
  if (from) path += `&from=${from}`;
  if (to)   path += `&to=${to}`;

  const tbody = document.getElementById('att-tbody');
  ui.showSkeleton('att-tbody', 6);

  try {
    const records = await api.get(path);
    if (!records.length) {
      tbody.innerHTML = `<tr><td colspan="6"><div class="empty-state"><div class="empty-icon">📋</div><h3>No records found</h3><p>Mark attendance to see reports here</p></div></td></tr>`;
      return;
    }
    tbody.innerHTML = records.map(r => {
      const pct = r.percentage || 0;
      const pctClass = pct >= 75 ? 'badge-success' : pct >= 50 ? 'badge-lab' : 'badge-danger';
      return `<tr>
        <td>${r.date}</td>
        <td><strong>${r.subject_code}</strong></td>
        <td>Slot ${r.slot}</td>
        <td>${r.present_students.length} / ${r.total_students}</td>
        <td><span class="badge ${pctClass}">${pct}%</span></td>
        <td style="font-size:12px;color:var(--text-muted)">${r.marked_at ? new Date(r.marked_at).toLocaleTimeString('en-IN', {hour:'2-digit',minute:'2-digit'}) : '—'}</td>
      </tr>`;
    }).join('');

    // Summary stats
    const avg = Math.round(records.reduce((a, r) => a + (r.percentage || 0), 0) / records.length);
    document.getElementById('att-total-classes').textContent = records.length;
    document.getElementById('att-avg-pct').textContent = avg + '%';
  } catch (e) {
    ui.toast(e.message, 'error');
    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;color:var(--text-muted);padding:40px">Failed to load report</td></tr>`;
  }
}

document.addEventListener('DOMContentLoaded', () => {
  // Default date to today
  const dateInput = document.getElementById('att-date');
  if (dateInput) dateInput.value = new Date().toISOString().split('T')[0];
});
