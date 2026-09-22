(function () {
    function formatTimeRange(start, end) {
        if (!start && !end) return '—';
        const s = start ? start.slice(0, 5) : '—';
        const e = end ? end.slice(0, 5) : '—';
        return `${s} - ${e}`;
    }

    function statusBadge(item) {
        const lectureStatus = (item?.lecture_status || '').toUpperCase();
        const marked = !!item?.attendance_marked;

        if (marked) return { label: 'Completed', cls: 'bg-success' };
        if (lectureStatus === 'ONGOING') return { label: 'In Progress', cls: 'bg-primary' };
        if (lectureStatus === 'ENDED') return { label: 'Ended', cls: 'bg-secondary' };
        return { label: lectureStatus || '—', cls: 'bg-light text-dark border' };
    }

    function setText(id, value) {
        const el = document.getElementById(id);
        if (!el) return;
        el.textContent = value ?? '—';
    }

    function renderRecentActivity(rows) {
        const tbody = document.getElementById('recentActivityBody');
        if (!tbody) return;

        const safeRows = Array.isArray(rows) ? rows : [];

        if (!safeRows.length) {
            tbody.innerHTML = `
                <tr>
                    <td class="ps-4" colspan="4">
                        <div class="text-muted small py-3">No activity yet for today.</div>
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = safeRows
            .map((r) => {
                const subject = r?.subject || '—';
                const time = formatTimeRange(r?.start_time, r?.end_time);
                const badge = statusBadge(r);
                return `
                    <tr>
                        <td class="ps-4">${r?.activity || 'Lecture'}</td>
                        <td>${subject}</td>
                        <td>${time}</td>
                        <td><span class="badge ${badge.cls}">${badge.label}</span></td>
                    </tr>
                `;
            })
            .join('');
    }

    async function loadDashboard() {
        try {
            const data = await window.apiGet('/api/faculty/dashboard/summary');

            setText('assignedSubjectsValue', data?.assigned_subjects_count);
            setText('totalStudentsValue', data?.total_students);
            setText('lecturesTodayValue', data?.lectures_today);
            setText('attendancePendingValue', data?.attendance_pending);
            renderRecentActivity(data?.recent_activity);
        } catch (err) {
            const msg = window.getApiErrorMessage(err, 'Failed to load dashboard');
            setText('assignedSubjectsValue', '—');
            setText('totalStudentsValue', '—');
            setText('lecturesTodayValue', '—');
            setText('attendancePendingValue', '—');
            renderRecentActivity([]);
            // Keep it low-noise: log for debugging only.
            console.error(msg);
        }
    }

    document.addEventListener('DOMContentLoaded', loadDashboard);
})();
