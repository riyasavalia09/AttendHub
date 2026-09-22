document.addEventListener('DOMContentLoaded', function () {
    const refreshBtn = document.getElementById('refreshLecturesBtn');
    if (refreshBtn) refreshBtn.addEventListener('click', loadTodayLectures);

    const closeMarkBtn = document.getElementById('closeMarkPanelBtn');
    if (closeMarkBtn) closeMarkBtn.addEventListener('click', hidePanels);

    const closePreviewBtn = document.getElementById('closePreviewPanelBtn');
    if (closePreviewBtn) closePreviewBtn.addEventListener('click', hidePanels);

    const submitBtn = document.getElementById('submitAttendanceBtn');
    if (submitBtn) {
        submitBtn.addEventListener('click', async () => {
            if (!selectedLectureId) {
                if (typeof window.showToast === 'function') {
                    window.showToast({
                        type: 'warning',
                        title: 'Select Lecture',
                        message: 'Please select a lecture to mark attendance.',
                    });
                }
                return;
            }

            const ok = typeof window.glassConfirm === 'function'
                ? await window.glassConfirm({
                    title: 'Confirm Submission',
                    message: 'Finalize attendance for this lecture? This action cannot be undone.',
                    confirmText: 'Submit',
                    cancelText: 'Cancel',
                    tone: 'danger',
                })
                : true;

            if (!ok) return;
            await submitAttendance();
        });
    }

    loadTodayLectures();
});

let studentsData = [];
let selectedLectureId = null;

function hidePanels() {
    const markPanel = document.getElementById('markPanel');
    const previewPanel = document.getElementById('previewPanel');
    if (markPanel) markPanel.style.display = 'none';
    if (previewPanel) previewPanel.style.display = 'none';
}

async function loadTodayLectures() {
    hidePanels();
    selectedLectureId = null;
    studentsData = [];

    const body = document.getElementById('todayLecturesBody');
    if (body) body.innerHTML = '<tr><td colspan="4" class="text-center text-muted py-4">Loading...</td></tr>';

    try {
        const lectures = await apiGet('/api/faculty/attendance/today');
        renderTodayLectures(lectures);
    } catch (error) {
        console.error('Failed to load today lectures', error);
        if (body) body.innerHTML = `<tr><td colspan="4" class="text-center text-danger py-4">${getApiErrorMessage(error, 'Failed to load lectures')}</td></tr>`;
    }
}

function renderTodayLectures(lectures) {
    const body = document.getElementById('todayLecturesBody');
    if (!body) return;

    body.innerHTML = '';

    if (!Array.isArray(lectures) || lectures.length === 0) {
        body.innerHTML = '<tr><td colspan="4" class="text-center text-muted py-4">No lectures found for today. Start a lecture first.</td></tr>';
        return;
    }

    lectures.forEach(l => {
        const timeText = `${formatTime(l.start_time)} - ${formatTime(l.end_time)}`;
        const lectureStatus = (l.status || l.lecture_status || '').toUpperCase();
        const isOngoing = lectureStatus === 'ONGOING';
        const isMarked = lectureStatus === 'MARKED';
        const isNotStarted = lectureStatus === 'NOT_STARTED';

        const statusBadge = isMarked
            ? '<span class="badge bg-secondary">Marked</span>'
            : (isOngoing
                ? '<span class="badge bg-warning text-dark">Ongoing</span>'
                : (isNotStarted
                    ? '<span class="badge bg-info text-dark">Not Started</span>'
                    : `<span class="badge bg-dark">${escapeHtml(lectureStatus || 'N/A')}</span>`));

        let actionBtn;
        if (isOngoing && l.lecture_id) {
            actionBtn = `<button class="btn btn-sm btn-primary" data-action="mark" data-lecture-id="${l.lecture_id}">Mark Attendance</button>`;
        } else if (isMarked && l.lecture_id) {
            actionBtn = `<button class="btn btn-sm btn-outline-light border" data-action="preview" data-lecture-id="${l.lecture_id}">Preview</button>`;
        } else if (isNotStarted && l.timetable_id) {
            actionBtn = `<button class="btn btn-sm btn-outline-primary" data-action="start" data-timetable-id="${l.timetable_id}">Start Lecture</button>`;
        } else {
            actionBtn = `<button class="btn btn-sm btn-outline-secondary" disabled>No Action</button>`;
        }

        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="fw-bold">${escapeHtml(l.subject || '')}</td>
            <td>${escapeHtml(timeText)}</td>
            <td>${statusBadge}</td>
            <td class="text-end">${actionBtn}</td>
        `;
        body.appendChild(row);
    });

    body.querySelectorAll('button[data-action]').forEach(btn => {
        btn.addEventListener('click', async () => {
            const action = btn.getAttribute('data-action');

            if (action === 'mark') {
                const lectureId = parseInt(btn.getAttribute('data-lecture-id'), 10);
                if (lectureId) startMarkFlow(lectureId);
            }
            if (action === 'preview') {
                const lectureId = parseInt(btn.getAttribute('data-lecture-id'), 10);
                if (lectureId) previewAttendance(lectureId);
            }
            if (action === 'start') {
                const timetableId = parseInt(btn.getAttribute('data-timetable-id'), 10);
                if (timetableId) await startLectureFromAttendancePage(timetableId);
            }
        });
    });
}

async function startLectureFromAttendancePage(timetableId) {
    try {
        const data = await apiPostJson('/api/faculty/lecture/start', { timetable_id: timetableId });
        if (typeof window.showToast === 'function') {
            window.showToast({ type: 'success', title: 'Lecture Started', message: 'You can now mark attendance.' });
        }

        await loadTodayLectures();

        if (data && data.lecture_id) {
            await startMarkFlow(data.lecture_id);
        }
    } catch (error) {
        console.error('Failed to start lecture', error);
        if (typeof window.showToast === 'function') {
            window.showToast({ type: 'error', title: 'Error', message: getApiErrorMessage(error, 'Failed to start lecture') });
        }
    }
}

async function startMarkFlow(lectureId) {
    hidePanels();
    selectedLectureId = lectureId;

    const markPanel = document.getElementById('markPanel');
    if (markPanel) markPanel.style.display = 'block';

    const tbody = document.getElementById('studentTableBody');
    if (tbody) tbody.innerHTML = '<tr><td colspan="3" class="text-center text-muted py-4">Loading students...</td></tr>';

    try {
        studentsData = await apiGet(`/api/faculty/attendance/students?lecture_id=${encodeURIComponent(String(lectureId))}`);
        renderStudentsForMarking(studentsData);
    } catch (error) {
        console.error('Failed to load students', error);
        if (tbody) tbody.innerHTML = `<tr><td colspan="3" class="text-center text-danger py-4">${getApiErrorMessage(error, 'Failed to load students')}</td></tr>`;
    }
}

function renderStudentsForMarking(students) {
    const tbody = document.getElementById('studentTableBody');
    if (!tbody) return;

    tbody.innerHTML = '';
    if (!Array.isArray(students) || students.length === 0) {
        tbody.innerHTML = '<tr><td colspan="3" class="text-center text-muted py-4">No students found for this class.</td></tr>';
        return;
    }

    students.forEach(student => {
        const enrollment = student.enrollment_no || 'N/A';
        const name = student.name || '';
        const id = student.student_id;
        const initials = (name || 'NA').split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();

        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="fw-bold text-secondary">${escapeHtml(enrollment)}</td>
            <td>
                <div class="d-flex align-items-center">
                    <div class="rounded-circle bg-light d-flex align-items-center justify-content-center me-3 border" style="width: 35px; height: 35px;">
                        <span class="small fw-bold text-muted">${escapeHtml(initials)}</span>
                    </div>
                    <span>${escapeHtml(name)}</span>
                </div>
            </td>
            <td class="text-center">
                <div class="btn-group" role="group">
                    <input type="radio" class="btn-check" name="status_${id}" id="p_${id}" value="PRESENT" checked>
                    <label class="btn btn-outline-success btn-sm px-3" for="p_${id}">Present</label>

                    <input type="radio" class="btn-check" name="status_${id}" id="a_${id}" value="ABSENT">
                    <label class="btn btn-outline-danger btn-sm px-3" for="a_${id}">Absent</label>
                </div>
            </td>
        `;
        tbody.appendChild(row);
    });
}

async function previewAttendance(lectureId) {
    hidePanels();

    const previewPanel = document.getElementById('previewPanel');
    if (previewPanel) previewPanel.style.display = 'block';

    const tbody = document.getElementById('previewTableBody');
    if (tbody) tbody.innerHTML = '<tr><td colspan="3" class="text-center text-muted py-4">Loading preview...</td></tr>';

    try {
        const rows = await apiGet(`/api/faculty/attendance/history?lecture_id=${encodeURIComponent(String(lectureId))}`);
        renderPreview(rows);
    } catch (error) {
        console.error('Failed to load preview', error);
        if (tbody) tbody.innerHTML = `<tr><td colspan="3" class="text-center text-danger py-4">${getApiErrorMessage(error, 'Failed to load preview')}</td></tr>`;
    }
}

function renderPreview(rows) {
    const tbody = document.getElementById('previewTableBody');
    if (!tbody) return;

    tbody.innerHTML = '';
    if (!Array.isArray(rows) || rows.length === 0) {
        tbody.innerHTML = '<tr><td colspan="3" class="text-center text-muted py-4">No attendance found.</td></tr>';
        return;
    }

    rows.forEach(r => {
        const enrollment = r.enrollment_no || 'N/A';
        const name = r.student_name || '';
        const status = r.status || '';
        const badge = status === 'PRESENT'
            ? '<span class="badge bg-success">PRESENT</span>'
            : '<span class="badge bg-danger">ABSENT</span>';

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td class="fw-bold text-secondary">${escapeHtml(enrollment)}</td>
            <td>${escapeHtml(name)}</td>
            <td class="text-center">${badge}</td>
        `;
        tbody.appendChild(tr);
    });
}

async function submitAttendance() {
    if (!selectedLectureId) {
        if (typeof window.showToast === 'function') {
            window.showToast({ type: 'warning', title: 'Select Lecture', message: 'Please select a lecture to mark attendance.' });
        }
        return;
    }

    // Connect Button Feedback
    let submitBtn = document.getElementById('submitAttendanceBtn');
    if (!submitBtn) {
        const buttons = Array.from(document.querySelectorAll('button'));
        submitBtn = buttons.find(b => b.textContent.includes('Submit Attendance'));
    }

    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Submitting...';
    }

    // Gather Data
    const attendanceList = studentsData.map(student => {
        const id = student.student_id;
        // Find checked radio
        const presentRadio = document.getElementById(`p_${id}`);
        const status = presentRadio && presentRadio.checked ? 'PRESENT' : 'ABSENT';

        return {
            student_id: id,
            status: status
        };
    });

    const payload = {
        lecture_id: parseInt(String(selectedLectureId), 10),
        students: attendanceList
    };

    try {
        const { data, payload: responsePayload } = await apiRequest('/api/faculty/attendance/mark', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const countText = (data && typeof data.count !== 'undefined') ? ` (${data.count} processed)` : '';
        if (typeof window.showToast === 'function') {
            window.showToast({
                type: 'success',
                title: 'Submitted',
                message: `${(responsePayload && responsePayload.message) || 'Attendance submitted'}${countText}`
            });
        }
        hidePanels();
        await loadTodayLectures();
    } catch (error) {
        console.error('Error:', error);
        if (typeof window.showToast === 'function') {
            window.showToast({ type: 'error', title: 'Error', message: getApiErrorMessage(error, 'Submission failed') });
        }
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = 'Submit Attendance';
        }
    }
}

function formatTime(timeStr) {
    if (!timeStr) return '';
    const parts = String(timeStr).split(':');
    let h = parseInt(parts[0], 10);
    const m = parts[1] || '00';
    const ampm = h >= 12 ? 'PM' : 'AM';
    h = h % 12;
    h = h ? h : 12;
    return `${h}:${m} ${ampm}`;
}

function escapeHtml(str) {
    return String(str)
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#039;');
}
