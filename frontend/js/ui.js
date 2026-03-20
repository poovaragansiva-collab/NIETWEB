/* ── UI Utilities ──────────────────────────────────── */

const ui = {
  // ── Toast ──────────────────────────────────────────
  toast(message, type = 'info', duration = 4000) {
    const icons = { success: '✓', error: '✕', info: 'ℹ️', warning: '⚠' };
    let container = document.getElementById('toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      container.className = 'toast-container';
      document.body.appendChild(container);
    }
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
      <span class="toast-icon">${icons[type] || 'ℹ️'}</span>
      <span class="toast-msg">${message}</span>
      <button class="toast-close" onclick="this.parentElement.remove()">✕</button>
    `;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), duration);
  },

  // ── Modal ──────────────────────────────────────────
  modal({ title, content, confirmText = 'Confirm', cancelText = 'Cancel', onConfirm, onCancel, wide = false } = {}) {
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.innerHTML = `
      <div class="modal${wide ? ' modal-wide' : ''}">
        <div class="modal-header">
          <h2>${title}</h2>
          <button class="modal-close">✕</button>
        </div>
        <div class="modal-body">${content}</div>
        ${onConfirm ? `
        <div class="modal-footer">
          <button class="btn btn-secondary" id="modal-cancel">${cancelText}</button>
          <button class="btn btn-primary" id="modal-confirm">${confirmText}</button>
        </div>` : ''}
      </div>`;

    document.body.appendChild(overlay);
    document.body.style.overflow = 'hidden';

    const close = () => {
      overlay.remove();
      document.body.style.overflow = '';
    };

    overlay.querySelector('.modal-close').onclick = close;
    overlay.addEventListener('click', e => { if (e.target === overlay) close(); });

    if (onConfirm) {
      overlay.querySelector('#modal-confirm').onclick = async () => {
        await onConfirm(overlay);
        close();
      };
      const cancelBtn = overlay.querySelector('#modal-cancel');
      if (cancelBtn) cancelBtn.onclick = () => { if (onCancel) onCancel(); close(); };
    }

    return overlay;
  },

  // ── Confirm dialog ─────────────────────────────────
  confirm(message) {
    return new Promise(resolve => {
      const overlay = ui.modal({
        title: 'Confirm Action',
        content: `<p style="color:var(--text-secondary);font-size:15px">${message}</p>`,
        confirmText: 'Delete',
        onConfirm: () => resolve(true),
        onCancel:  () => resolve(false),
      });
      // Override confirm button style to danger
      overlay.querySelector('#modal-confirm').className = 'btn btn-danger';
    });
  },

  // ── Skeleton loader ────────────────────────────────
  showSkeleton(tbodyId, cols = 5, rows = 5) {
    const el = document.getElementById(tbodyId);
    if (!el) return;
    el.innerHTML = Array.from({ length: rows }, () =>
      `<tr>${Array.from({ length: cols }, () =>
        `<td><span class="skeleton skeleton-text" style="width:${60 + Math.random() * 30}%"></span></td>`
      ).join('')}</tr>`
    ).join('');
  },

  // ── Sidebar toggle ─────────────────────────────────
  initSidebar() {
    const sidebar = document.getElementById('sidebar');
    const layout = document.getElementById('layout');
    const toggle = document.getElementById('sidebar-toggle');
    if (!sidebar || !toggle) return;

    const collapsed = localStorage.getItem('sidebar-collapsed') === 'true';
    if (collapsed) {
      sidebar.classList.add('collapsed');
      layout.classList.add('sidebar-collapsed');
    }

    toggle.addEventListener('click', () => {
      sidebar.classList.toggle('collapsed');
      layout.classList.toggle('sidebar-collapsed');
      localStorage.setItem('sidebar-collapsed', sidebar.classList.contains('collapsed'));
    });
  },

  // ── Live clock ─────────────────────────────────────
  initClock() {
    const el = document.getElementById('header-time');
    if (!el) return;
    const update = () => {
      el.textContent = new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
    };
    update();
    setInterval(update, 1000);
  },

  // ── Format date ────────────────────────────────────
  formatDate(str) {
    if (!str) return '—';
    return new Date(str).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
  },

  // ── Debounce ───────────────────────────────────────
  debounce(fn, ms = 300) {
    let t;
    return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); };
  },

  // ── Initialize common UI ──────────────────────────
  init() {
    ui.initSidebar();
    ui.initClock();
  },
};

// Auto-init on DOM ready
document.addEventListener('DOMContentLoaded', () => ui.init());
