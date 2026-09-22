let __historyRows = [];
let __subjectsLoaded = false;

document.addEventListener('DOMContentLoaded', function () {
    loadHistory({});
    wireFilters();
    wireExport();
});

function buildHistoryUrl(filters) {
    const params = new URLSearchParams();
    if (filters?.subject) params.set('subject', filters.subject);
    if (filters?.from_date) params.set('from_date', filters.from_date);
    if (filters?.to_date) params.set('to_date', filters.to_date);
    const qs = params.toString();
    return '/api/faculty/attendance/history' + (qs ? `?${qs}` : '');
}

function buildExportUrl(filters) {
    const params = new URLSearchParams();
    if (filters?.subject) params.set('subject', filters.subject);
    if (filters?.from_date) params.set('from_date', filters.from_date);
    if (filters?.to_date) params.set('to_date', filters.to_date);
    const qs = params.toString();
    return '/api/faculty/attendance/history/export' + (qs ? `?${qs}` : '');
}

function getCurrentFilters() {
    return {
        subject: document.getElementById('subjectFilter')?.value || '',
        from_date: document.getElementById('fromDateFilter')?.value || '',
        to_date: document.getElementById('toDateFilter')?.value || ''
    };
}

async function loadHistory(filters) {
    try {
        const history = await apiGet(buildHistoryUrl(filters || {}));
        __historyRows = Array.isArray(history) ? history : [];

        // Populate subject list once from the unfiltered dataset.
        if (!__subjectsLoaded && (!filters || (!filters.subject && !filters.from_date && !filters.to_date))) {
            populateSubjectFilter(__historyRows);
            __subjectsLoaded = true;
        }

        renderTable(__historyRows);
    } catch (error) {
        console.error('Error:', error);
    }
}

function wireFilters() {
    const subject = document.getElementById('subjectFilter');
    const fromDate = document.getElementById('fromDateFilter');
    const toDate = document.getElementById('toDateFilter');
    const applyBtn = document.getElementById('applyFiltersBtn');

    const refresh = () => loadHistory(getCurrentFilters());

    subject?.addEventListener('change', refresh);
    fromDate?.addEventListener('change', refresh);
    toDate?.addEventListener('change', refresh);
    applyBtn?.addEventListener('click', refresh);
}

function wireExport() {
    const exportBtn = document.getElementById('exportHistoryBtn');
    if (!exportBtn) return;

    exportBtn.addEventListener('click', () => {
        const url = buildExportUrl(getCurrentFilters());
        // Use navigation so browser handles file download.
        window.location.href = url;
    });
}

function populateSubjectFilter(rows) {
    const select = document.getElementById('subjectFilter');
    if (!select) return;

    const subjects = Array.from(
        new Set((rows || []).map((r) => (r?.subject || '').trim()).filter(Boolean))
    ).sort();

    const current = select.value;
    select.innerHTML = '<option value="">All Subjects</option>' + subjects.map((s) => `<option value="${escapeHtml(s)}">${escapeHtml(s)}</option>`).join('');
    // keep selection if still valid
    if (subjects.includes(current)) select.value = current;
}

function renderTable(data) {
    const tbody = document.getElementById('historyTableBody');
    if (!tbody) return;
    
    tbody.innerHTML = '';

    if (data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center py-4 text-muted">No attendance history found.</td></tr>';
        return;
    }

    data.forEach(item => {
        const dateObj = new Date(item.lecture_date);
        const formattedDate = dateObj.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
        
        // Time Formatting
        const start = formatTime(item.start_time);
        const end = formatTime(item.end_time);

        // Stats
        const present = item.stats ? item.stats.present : 0;
        const total = item.stats ? item.stats.total : 0;
        
        // Status Badge
        const normalizedStatus = String(item?.status || '').toUpperCase();
        let statusBadge = '';
        if (normalizedStatus === 'MARKED' || normalizedStatus === 'ENDED') {
            statusBadge = '<span class="badge bg-success">Submitted</span>';
        } else if (normalizedStatus === 'ONGOING') {
            statusBadge = '<span class="badge bg-warning text-dark">Ongoing</span>';
        } else if (!normalizedStatus && total > 0) {
            // Backward-compat for legacy rows with blank enum value.
            statusBadge = '<span class="badge bg-success">Submitted</span>';
        } else {
            statusBadge = '<span class="badge bg-secondary">Unknown</span>';
        }

        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="fw-bold">${formattedDate}</td>
            <td>
                <span class="d-block fw-bold text-dark">${item.subject}</span>
            </td>
            <td>${start} - ${end}</td>
            <td class="text-center"><span class="badge bg-primary">${present} / ${total}</span></td>
            <td>${statusBadge}</td>
            <td class="text-end">
                <button class="btn btn-sm btn-link text-decoration-none" data-lecture-id="${item.lecture_id}">View</button>
            </td>
        `;
        tbody.appendChild(row);
    });

    tbody.querySelectorAll('button[data-lecture-id]').forEach((btn) => {
        btn.addEventListener('click', () => {
            const id = btn.getAttribute('data-lecture-id');
            viewDetails(Number(id));
        });
    });
}

function formatTime(timeStr) {
    // 09:00:00 -> 09:00 AM
    if (!timeStr) return '';
    // If it's a seconds format, strip seconds
    // Assume input HH:MM:SS or HH:MM
    const parts = timeStr.split(':');
    let h = parseInt(parts[0], 10);
    const m = parts[1];
    
    const ampm = h >= 12 ? 'PM' : 'AM';
    h = h % 12;
    h = h ? h : 12; // 0 should be 12
    return `${h}:${m} ${ampm}`;
}

function escapeHtml(str) {
    return String(str ?? '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#039;');
}

function setText(id, value) {
    const el = document.getElementById(id);
    if (!el) return;
    el.textContent = value ?? '—';
}

async function viewDetails(lectureId) {
    if (!lectureId) return;

    const modalEl = document.getElementById('attendanceDetailsModal');
    const tbody = document.getElementById('attendanceDetailsBody');
    if (!modalEl || !tbody) return;

    // Try to find lecture row for meta
    const lectureRow = (__historyRows || []).find((r) => Number(r?.lecture_id) === Number(lectureId));
    const dateStr = lectureRow?.lecture_date ? new Date(lectureRow.lecture_date).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }) : '';
    const subject = lectureRow?.subject || '';
    const start = formatTime(lectureRow?.start_time);
    const end = formatTime(lectureRow?.end_time);

    setText('attendanceDetailsMeta', `${subject}${dateStr ? ' • ' + dateStr : ''}${start || end ? ' • ' + start + ' - ' + end : ''}`);
    setText('attendanceDetailsCount', '—');
    setText('attendanceDetailsPresent', '—');
    setText('attendanceDetailsAbsent', '—');
    tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted py-4">Loading...</td></tr>';

    const modal = window.bootstrap?.Modal?.getOrCreateInstance(modalEl);
    modal?.show();

    try {
        const details = await apiGet(`/api/faculty/attendance/history?lecture_id=${encodeURIComponent(lectureId)}`);
        const rows = Array.isArray(details) ? details : [];

        const total = rows.length;
        const present = rows.filter((r) => String(r?.status || '').toUpperCase() === 'PRESENT').length;
        const absent = rows.filter((r) => String(r?.status || '').toUpperCase() === 'ABSENT').length;

        setText('attendanceDetailsCount', `Total: ${total}`);
        setText('attendanceDetailsPresent', `Present: ${present}`);
        setText('attendanceDetailsAbsent', `Absent: ${absent}`);

        if (!rows.length) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted py-4">No attendance rows found for this lecture.</td></tr>';
            return;
        }

        tbody.innerHTML = rows
            .map((r) => {
                const status = String(r?.status || '').toUpperCase();
                const badge = status === 'PRESENT'
                    ? '<span class="badge bg-success">PRESENT</span>'
                    : '<span class="badge bg-danger">ABSENT</span>';

                return `
                    <tr>
                        <td class="fw-bold">${escapeHtml(r?.enrollment_no || '')}</td>
                        <td>${escapeHtml(r?.student_name || '')}</td>
                        <td>${escapeHtml(r?.department || '')}</td>
                        <td>${r?.semester != null ? escapeHtml(r.semester) : ''}</td>
                        <td>${badge}</td>
                    </tr>
                `;
            })
            .join('');
    } catch (error) {
        console.error('Error:', error);
        const message = (window.getApiErrorMessage && window.getApiErrorMessage(error, 'Failed to load details')) || 'Failed to load details';
        tbody.innerHTML = `<tr><td colspan="5" class="text-center text-danger py-4">${escapeHtml(message)}</td></tr>`;
    }
}
