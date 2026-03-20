/* ── Staff Management JS ────────────────────────────── */
let allStaff = [];

const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
const SLOTS = [1, 2, 3, 4, 5, 6];

async function loadStaff(filter = '') {
  const tbody = document.getElementById('staff-tbody');
  ui.showSkeleton('staff-tbody', 5);
  try {
    allStaff = await api.get('/staff');
    renderStaff(allStaff, filter);
    document.getElementById('staff-count').textContent = allStaff.length;
  } catch (e) {
    ui.toast('Failed to load staff: ' + e.message, 'error');
    tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;color:var(--text-muted);padding:40px">Failed to load data</td></tr>`;
  }
}

function renderStaff(list, filter = '') {
  const tbody = document.getElementById('staff-tbody');
  const filtered = filter
    ? list.filter(s => s.name.toLowerCase().includes(filter) || s.department.toLowerCase().includes(filter) || s.email.toLowerCase().includes(filter))
    : list;

  if (!filtered.length) {
    tbody.innerHTML = `<tr><td colspan="5"><div class="empty-state"><div class="empty-icon">👥</div><h3>No staff found</h3><p>Add your first staff member to get started</p></div></td></tr>`;
    return;
  }

  tbody.innerHTML = filtered.map(s => `
    <tr class="animate-fade-in">
      <td>
        <div style="display:flex;align-items:center;gap:12px">
          <div style="width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,var(--accent-primary),var(--accent-purple));display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:600;flex-shrink:0">
            ${s.name.charAt(0).toUpperCase()}
          </div>
          <div>
            <div style="font-weight:500">${s.name}</div>
            <div style="font-size:12px;color:var(--text-muted)">${s.email}</div>
          </div>
        </div>
      </td>
      <td><span class="badge badge-${s.department.toLowerCase()}">${s.department}</span></td>
      <td>${(s.subjects || []).slice(0, 3).map(c => `<span class="badge badge-theory" style="margin:2px">${c}</span>`).join('') || '—'}</td>
      <td style="font-size:13px;color:var(--text-secondary)">${Object.keys(s.availability || {}).length} days configured</td>
      <td>
        <div class="actions">
          <button class="btn btn-secondary btn-sm" onclick="editStaff('${s.id}')">Edit</button>
          <button class="btn btn-danger btn-sm" onclick="deleteStaff('${s.id}','${s.name}')">Delete</button>
        </div>
      </td>
    </tr>
  `).join('');
}

function buildAvailabilityGrid(existing = {}) {
  return `
    <div style="overflow-x:auto">
      <table style="border-collapse:collapse;font-size:12px;width:100%">
        <thead>
          <tr>
            <th style="padding:6px 10px;text-align:left;color:var(--text-muted)">Day</th>
            ${SLOTS.map(s => `<th style="padding:6px 8px;text-align:center;color:var(--text-muted)">Slot ${s}</th>`).join('')}
          </tr>
        </thead>
        <tbody>
          ${DAYS.map(day => `
            <tr>
              <td style="padding:6px 10px;font-weight:500;color:var(--text-secondary)">${day}</td>
              ${SLOTS.map(slot => {
                const checked = (existing[day] || []).includes(slot) ? 'checked' : '';
                return `<td style="padding:6px 8px;text-align:center">
                  <input type="checkbox" class="avail-check" data-day="${day}" data-slot="${slot}" ${checked}
                    style="width:16px;height:16px;accent-color:var(--accent-primary);cursor:pointer">
                </td>`;
              }).join('')}
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `;
}

function readAvailability(container) {
  const availability = {};
  container.querySelectorAll('.avail-check:checked').forEach(cb => {
    const day = cb.dataset.day;
    const slot = parseInt(cb.dataset.slot);
    if (!availability[day]) availability[day] = [];
    availability[day].push(slot);
  });
  return availability;
}

function openAddStaff() {
  ui.modal({
    title: 'Add Staff Member',
    content: `
      <div class="grid-2">
        <div class="input-group"><label>Full Name *</label><input id="s-name" placeholder="Dr. Ramesh Kumar"></div>
        <div class="input-group"><label>Department *</label>
          <select id="s-dept">
            <option value="CSE">Computer Science (CSE)</option>
            <option value="ECE">Electronics (ECE)</option>
            <option value="MECH">Mechanical (MECH)</option>
            <option value="CIVIL">Civil</option>
            <option value="EEE">Electrical (EEE)</option>
          </select>
        </div>
      </div>
      <div class="input-group"><label>Email *</label><input id="s-email" type="email" placeholder="name@college.edu"></div>
      <div class="input-group"><label>Subject Codes (comma separated)</label><input id="s-subjects" placeholder="CS101, CS203"></div>
      <div style="margin-bottom:12px">
        <label style="font-size:13px;color:var(--text-secondary);font-weight:500">Availability</label>
        <div style="margin-top:8px">${buildAvailabilityGrid()}</div>
      </div>
    `,
    confirmText: 'Add Staff',
    onConfirm: async (overlay) => {
      const name     = overlay.querySelector('#s-name').value.trim();
      const dept     = overlay.querySelector('#s-dept').value;
      const email    = overlay.querySelector('#s-email').value.trim();
      const subjects = overlay.querySelector('#s-subjects').value.split(',').map(s => s.trim()).filter(Boolean);
      const availability = readAvailability(overlay);

      if (!name || !email) { ui.toast('Name and email are required', 'error'); throw new Error('validation'); }

      await api.post('/staff', { name, department: dept, email, subjects, availability });
      ui.toast(`${name} added successfully`, 'success');
      await loadStaff();
    },
  });
}

async function editStaff(id) {
  const staff = allStaff.find(s => s.id === id);
  if (!staff) return;

  ui.modal({
    title: 'Edit Staff Member',
    content: `
      <div class="grid-2">
        <div class="input-group"><label>Full Name</label><input id="s-name" value="${staff.name}"></div>
        <div class="input-group"><label>Department</label>
          <select id="s-dept">
            ${['CSE','ECE','MECH','CIVIL','EEE'].map(d => `<option value="${d}" ${d===staff.department?'selected':''}>${d}</option>`).join('')}
          </select>
        </div>
      </div>
      <div class="input-group"><label>Email</label><input id="s-email" type="email" value="${staff.email}"></div>
      <div class="input-group"><label>Subject Codes</label><input id="s-subjects" value="${(staff.subjects||[]).join(', ')}"></div>
      <div style="margin-bottom:12px">
        <label style="font-size:13px;color:var(--text-secondary);font-weight:500">Availability</label>
        <div style="margin-top:8px">${buildAvailabilityGrid(staff.availability || {})}</div>
      </div>
    `,
    confirmText: 'Save Changes',
    onConfirm: async (overlay) => {
      const name     = overlay.querySelector('#s-name').value.trim();
      const dept     = overlay.querySelector('#s-dept').value;
      const email    = overlay.querySelector('#s-email').value.trim();
      const subjects = overlay.querySelector('#s-subjects').value.split(',').map(s => s.trim()).filter(Boolean);
      const availability = readAvailability(overlay);

      await api.put(`/staff/${id}`, { name, department: dept, email, subjects, availability });
      ui.toast('Staff updated successfully', 'success');
      await loadStaff();
    },
  });
}

async function deleteStaff(id, name) {
  const ok = await ui.confirm(`Are you sure you want to delete <strong>${name}</strong>? This action cannot be undone.`);
  if (!ok) return;
  try {
    await api.delete(`/staff/${id}`);
    ui.toast(`${name} deleted`, 'success');
    await loadStaff();
  } catch (e) {
    ui.toast(e.message, 'error');
  }
}

// Search
document.addEventListener('DOMContentLoaded', () => {
  loadStaff();
  const searchInput = document.getElementById('staff-search');
  if (searchInput) {
    searchInput.addEventListener('input', ui.debounce(e => renderStaff(allStaff, e.target.value.toLowerCase()), 250));
  }
});
