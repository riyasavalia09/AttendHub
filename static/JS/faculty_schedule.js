(function () {
    const DAY_LABELS = {
        MON: 'Monday',
        TUE: 'Tuesday',
        WED: 'Wednesday',
        THU: 'Thursday',
        FRI: 'Friday',
        SAT: 'Saturday',
        SUN: 'Sunday'
    };

    function getTodayCode() {
        const d = new Date();
        const idx = d.getDay();
        // JS: 0 Sun..6 Sat
        const map = ['SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT'];
        return map[idx] || '';
    }

    function formatTimeRange(start, end) {
        const s = start ? String(start).slice(0, 5) : '—';
        const e = end ? String(end).slice(0, 5) : '—';
        return `${s} - ${e}`;
    }

    function renderRows(rows) {
        const tbody = document.getElementById('weeklyScheduleBody');
        if (!tbody) return;

        const items = Array.isArray(rows) ? rows : [];
        const todayCode = getTodayCode();

        if (!items.length) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="5">
                        <div class="text-muted small py-3">No timetable entries found.</div>
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = items
            .map((slot) => {
                const dayCode = (slot?.day || '').toUpperCase();
                const isToday = dayCode === todayCode;
                const dayLabel = DAY_LABELS[dayCode] || slot?.day || '—';
                const dept = slot?.department || '—';
                const sem = slot?.semester != null ? `Sem ${slot.semester}` : '—';
                const subject = slot?.subject || '—';
                const time = formatTimeRange(slot?.start_time, slot?.end_time);

                return `
                    <tr class="${isToday ? 'row-highlight' : ''}">
                        <td class="${isToday ? 'fw-bold text-primary' : ''}">${dayLabel}${isToday ? ' (Today)' : ''}</td>
                        <td><span class="fw-medium">${subject}</span></td>
                        <td>${time}</td>
                        <td>${dept} (${sem})</td>
                        <td><span class="badge bg-secondary">Scheduled</span></td>
                    </tr>
                `;
            })
            .join('');
    }

    async function loadSchedule() {
        try {
            const data = await window.apiGet('/api/faculty/schedule/weekly');
            renderRows(data);
        } catch (err) {
            console.error(window.getApiErrorMessage(err, 'Failed to load schedule'));
            renderRows([]);
        }
    }

    document.addEventListener('DOMContentLoaded', loadSchedule);
})();
