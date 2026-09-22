document.addEventListener('DOMContentLoaded', function() {
    loadTodaysLecture();

    const startBtn = document.getElementById('startLectureBtn');
    if (startBtn) {
        startBtn.addEventListener('click', handleLectureButtonClick);
    }
});

let currentTimetableId = null;

function todayKey() {
    // Per-tab storage is fine; include date so it resets daily.
    const d = new Date();
    const yyyy = d.getFullYear();
    const mm = String(d.getMonth() + 1).padStart(2, '0');
    const dd = String(d.getDate()).padStart(2, '0');
    return `${yyyy}-${mm}-${dd}`;
}

function completedKey() {
    return `completed_timetable_ids_${todayKey()}`;
}

function getCompletedTimetableIds() {
    try {
        const raw = sessionStorage.getItem(completedKey());
        const ids = raw ? JSON.parse(raw) : [];
        return Array.isArray(ids) ? ids : [];
    } catch (_) {
        return [];
    }
}

function markTimetableCompleted(timetableId) {
    const ids = new Set(getCompletedTimetableIds());
    ids.add(Number(timetableId));
    sessionStorage.setItem(completedKey(), JSON.stringify(Array.from(ids)));
}

async function loadTodaysLecture() {
    try {
        const [lectures, attendanceToday] = await Promise.all([
            apiGet('/api/faculty/schedule/today'),
            apiGet('/api/faculty/attendance/today').catch(() => [])
        ]);
            
        const container = document.getElementById('lectureCardContainer');
        if (!Array.isArray(lectures) || lectures.length === 0) {
            container.innerHTML = `
                <div class="alert alert-info text-center">
                    <i class="fas fa-calendar-times fa-2x mb-3"></i>
                    <p class="mb-0">No lectures scheduled for today.</p>
                </div>`;
            return;
        }

        const statusMap = new Map();
        (Array.isArray(attendanceToday) ? attendanceToday : []).forEach((item) => {
            if (!item || typeof item !== 'object') return;
            statusMap.set(Number(item.timetable_id), item);
        });

        // Prefer actionable slots first.
        const lecture = lectures.find((l) => {
            const row = statusMap.get(Number(l.timetable_id));
            const st = String(row?.status || '').toUpperCase();
            return st === 'NOT_STARTED' || st === 'ONGOING' || !st;
        }) || lectures[0];

        currentTimetableId = lecture.timetable_id;
        updateLectureCard(lecture);

        const currentStatusRow = statusMap.get(Number(currentTimetableId)) || null;
        const currentStatus = String(currentStatusRow?.status || '').toUpperCase();

        if (currentStatus === 'ONGOING') {
            if (currentStatusRow?.lecture_id) {
                sessionStorage.setItem('active_lecture_id', String(currentStatusRow.lecture_id));
                sessionStorage.setItem('active_timetable_id', String(currentTimetableId));
            }
            setLectureActiveUI();
            return;
        }

        if (currentStatus === 'MARKED' || currentStatus === 'ENDED') {
            setLectureCompletedUI();
            return;
        }

        // Default state: allow starting.
        sessionStorage.removeItem('active_lecture_id');
        sessionStorage.removeItem('active_timetable_id');
        setLectureInactiveUI();
    } catch (error) {
        console.error('Failed to load schedule', error);
    }
}

function updateLectureCard(lecture) {
    document.getElementById('subjectName').textContent = lecture.subject;
    document.getElementById('lectureTime').textContent = `${formatTime(lecture.start_time)} - ${formatTime(lecture.end_time)}`;
    // If faculty is logged in, department might not be in lecture object unless we joined.
    // The repo find_by_faculty SELECT * FROM timetable so no department.
    // We can hide it or leave static if not available.
}

function formatTime(timeStr) {
    // 09:00:00 -> 09:00 AM
    if (!timeStr) return '';
    const [hours, minutes] = timeStr.split(':');
    const h = parseInt(hours, 10);
    const m = parseInt(minutes, 10);
    const ampm = h >= 12 ? 'PM' : 'AM';
    const h12 = h % 12 || 12;
    return `${h12}:${m.toString().padStart(2, '0')} ${ampm}`;
}

async function startLecture() {
    if (!currentTimetableId) return;

    const btn = document.getElementById('startLectureBtn');
    const originalContent = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Starting...';

    try {
        const data = await apiPostJson('/api/faculty/lecture/start', { timetable_id: currentTimetableId });

        // 1. Store in sessionStorage
        sessionStorage.setItem('active_lecture_id', data.lecture_id);
        sessionStorage.setItem('active_timetable_id', currentTimetableId);

        // 2. Update UI
        setLectureActiveUI();

        if (typeof window.showToast === 'function') {
            window.showToast({
                type: 'success',
                title: 'Lecture Started',
                message: 'Student attendance is now enabled.'
            });
        }
    } catch (error) {
        console.error('Error starting lecture:', error);
        if (typeof window.showToast === 'function') {
            window.showToast({ type: 'error', title: 'Error', message: getApiErrorMessage(error, 'Failed to start lecture') });
        }
        btn.disabled = false;
        btn.innerHTML = originalContent;
    }
}

async function endLecture() {
    const lectureId = sessionStorage.getItem('active_lecture_id');
    if (!lectureId) return;

    const btn = document.getElementById('startLectureBtn');
    const originalContent = btn ? btn.innerHTML : '';
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Ending...';
    }

    try {
        await apiPostJson('/api/faculty/lecture/end', { lecture_id: parseInt(lectureId, 10) });
        // Mark this timetable slot as completed for today
        if (currentTimetableId) {
            markTimetableCompleted(currentTimetableId);
        }
        sessionStorage.removeItem('active_lecture_id');
        sessionStorage.removeItem('active_timetable_id');

        // Move to next lecture slot (if any)
        await loadTodaysLecture();
        if (typeof window.showToast === 'function') {
            window.showToast({ type: 'success', title: 'Session Ended', message: 'Lecture session ended.' });
        }
    } catch (error) {
        console.error('Error ending lecture:', error);
        if (typeof window.showToast === 'function') {
            window.showToast({ type: 'error', title: 'Error', message: getApiErrorMessage(error, 'Failed to end lecture') });
        }
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = originalContent;
        }
    }
}

function handleLectureButtonClick() {
    const activeLectureId = sessionStorage.getItem('active_lecture_id');
    if (activeLectureId) {
        endLecture();
    } else {
        startLecture();
    }
}

function setLectureActiveUI() {
    const btn = document.getElementById('startLectureBtn');
    const badge = document.getElementById('statusBadge');
    
    if (btn) {
        btn.innerHTML = '<i class="fas fa-stop me-2"></i><strong>End Session</strong>';
        btn.classList.remove('btn-primary');
        btn.classList.add('btn-danger');
        btn.disabled = false;
    }
    
    if (badge) {
        badge.className = 'badge bg-success text-white px-3 py-2 rounded-pill';
        badge.innerHTML = '<i class="fas fa-satellite-dish me-1"></i> Lecture Ongoing';
    }
}

function setLectureInactiveUI() {
    const btn = document.getElementById('startLectureBtn');
    const badge = document.getElementById('statusBadge');

    if (btn) {
        btn.innerHTML = '<i class="fas fa-play me-2"></i><strong>Start Lecture Session</strong>';
        btn.classList.remove('btn-danger');
        btn.classList.add('btn-primary');
        btn.disabled = false;
    }

    if (badge) {
        badge.className = 'badge bg-warning text-dark px-3 py-2 rounded-pill';
        badge.innerHTML = '<i class="fas fa-clock me-1"></i> Not Started';
    }
}

function setLectureCompletedUI() {
    const btn = document.getElementById('startLectureBtn');
    const badge = document.getElementById('statusBadge');

    if (btn) {
        btn.innerHTML = '<i class="fas fa-check me-2"></i><strong>Completed</strong>';
        btn.classList.remove('btn-primary');
        btn.classList.remove('btn-danger');
        btn.classList.add('btn-secondary');
        btn.disabled = true;
    }

    if (badge) {
        badge.className = 'badge bg-secondary text-white px-3 py-2 rounded-pill';
        badge.innerHTML = '<i class="fas fa-check-circle me-1"></i> Completed';
    }
}

function checkActiveSession() {
    // If page reload, check if we are already in session
    const active = sessionStorage.getItem('active_lecture_id');
    if (active) {
        setLectureActiveUI();
    }
}
