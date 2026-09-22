document.addEventListener('DOMContentLoaded', function () {
    loadStudentTimetable();
});

const DAY_ORDER = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'];
const DAY_LABEL = {
    MON: 'Monday',
    TUE: 'Tuesday',
    WED: 'Wednesday',
    THU: 'Thursday',
    FRI: 'Friday',
    SAT: 'Saturday',
    SUN: 'Sunday'
};

function formatTime(timeStr) {
    // 09:00:00 -> 9:00 AM
    if (!timeStr) return '';
    const parts = String(timeStr).split(':');
    let h = parseInt(parts[0], 10);
    const m = parts[1] ?? '00';
    const ampm = h >= 12 ? 'PM' : 'AM';
    h = h % 12;
    h = h ? h : 12;
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

async function loadStudentTimetable() {
    const tbody = document.getElementById('studentTimetableBody');
    if (!tbody) return;

    try {
        const rows = await apiGet('/api/student/timetable');
        const list = Array.isArray(rows) ? rows : [];

        // Today badge
        const todayBadge = document.getElementById('todayBadge');
        if (todayBadge) {
            const day = new Date().toLocaleDateString(undefined, { weekday: 'long' });
            todayBadge.innerHTML = `<i class="fas fa-calendar-day me-2"></i>Today is ${escapeHtml(day)}`;
        }

        tbody.innerHTML = '';

        if (list.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center p-4 text-muted">No timetable entries found.</td></tr>';
            return;
        }

        // Group by day
        const grouped = {};
        list.forEach((r) => {
            const day = r?.day;
            if (!day) return;
            if (!grouped[day]) grouped[day] = [];
            grouped[day].push(r);
        });

        const todayCode = DAY_ORDER[new Date().getDay() === 0 ? 6 : new Date().getDay() - 1]; // JS Sunday=0

        DAY_ORDER.forEach((dayCode) => {
            const dayRows = grouped[dayCode] || [];
            if (dayRows.length === 0) return;

            const isToday = dayCode === todayCode;
            const dayLabel = DAY_LABEL[dayCode] || dayCode;

            // Day header row
            const headerTr = document.createElement('tr');
            headerTr.className = isToday ? 'table-warning border-bottom-0' : 'table-light';
            headerTr.innerHTML = `
                <td colspan="5" class="ps-4 fw-bold small text-uppercase ${isToday ? 'text-dark bg-warning bg-opacity-10 border-start border-4 border-warning' : 'text-muted'}">
                    ${escapeHtml(dayLabel)}${isToday ? ' <span class="badge bg-warning text-dark ms-2">TODAY</span>' : ''}
                </td>
            `;
            tbody.appendChild(headerTr);

            dayRows.forEach((r, idx) => {
                const tr = document.createElement('tr');
                if (isToday) tr.classList.add('today-highlight');

                const start = formatTime(r?.start_time);
                const end = formatTime(r?.end_time);

                tr.innerHTML = `
                    <td class="ps-4 fw-bold ${isToday ? 'text-dark' : 'text-primary'}">${idx === 0 ? escapeHtml(dayLabel) : ''}</td>
                    <td class="fw-bold">${escapeHtml(r?.subject || '')}</td>
                    <td>${escapeHtml(start)} - ${escapeHtml(end)}</td>
                    <td>${escapeHtml(r?.faculty_name || '')}</td>
                    <td><span class="badge ${isToday ? 'bg-warning text-dark border border-warning' : 'bg-light text-dark border'}">—</span></td>
                `;
                tbody.appendChild(tr);
            });
        });
    } catch (error) {
        console.error('Error loading timetable:', error);
        const message = (window.getApiErrorMessage && window.getApiErrorMessage(error, 'Failed to load timetable')) || 'Failed to load timetable';
        tbody.innerHTML = `<tr><td colspan="5" class="text-center p-4 text-danger">${escapeHtml(message)}</td></tr>`;
    }
}
