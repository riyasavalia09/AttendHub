document.addEventListener('DOMContentLoaded', function() {
    loadDashboardStats();
});

async function loadDashboardStats() {
    try {
        const data = await apiGet('/api/student/dashboard/summary');
        updateDashboardUI(data);
    } catch (error) {
        console.error('Error:', error);
    }
}

function updateDashboardUI(data) {
    const student = data?.student || {};

    // Top/Welcome/Profile placeholders
    const name = student?.name || 'Student';
    const enrollment = student?.enrollment_no || '';
    const dept = student?.department || '';
    const sem = student?.semester != null ? String(student.semester) : '';

    const avatarUrl = `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=6CB1DA&color=fff&size=128`;
    const avatarUrlSmall = `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=random&size=64`;

    const nameTop = document.getElementById('studentNameTop');
    if (nameTop) nameTop.textContent = name;

    const welcome = document.getElementById('welcomeStudentName');
    if (welcome) welcome.textContent = name;

    const avatarTop = document.getElementById('studentAvatarTop');
    if (avatarTop) avatarTop.src = avatarUrlSmall;

    const avatarCard = document.getElementById('studentAvatarCard');
    if (avatarCard) avatarCard.src = avatarUrl;

    const nameCard = document.getElementById('studentNameCard');
    if (nameCard) nameCard.textContent = name;

    const deptSemCard = document.getElementById('studentDeptSemCard');
    if (deptSemCard) deptSemCard.textContent = `${dept}${dept && sem ? ' | ' : ''}${sem ? 'Semester ' + sem : ''}` || '—';

    const enrollCard = document.getElementById('studentEnrollmentCard');
    if (enrollCard) enrollCard.textContent = `Roll No: ${enrollment || '—'}`;

    // 1. Update Counts
    const subjectsEl = document.getElementById('totalSubjectsValue');
    if (subjectsEl) subjectsEl.textContent = data.total_subjects || 0;

    const overallEl = document.getElementById('overallAttendanceValue');
    if (overallEl) {
        const pct = data.overall_attendance || 0;
        overallEl.textContent = pct + '%';
        
        // Color coding
        overallEl.className = 'display-4 fw-bold ' + (pct >= 75 ? 'text-success' : pct >= 50 ? 'text-warning' : 'text-danger');
    }

    // 2. Render Recent Activity
    const activityTable = document.getElementById('recentActivityTable');
    if (activityTable) {
        const tbody = activityTable.querySelector('tbody');
        if (tbody) {
            tbody.innerHTML = ''; // Clear existing rows
            
            if (!data.recent_activity || data.recent_activity.length === 0) {
                 tbody.innerHTML = `
                    <tr>
                        <td colspan="5" class="text-center text-muted py-4">
                            <i class="fas fa-history mb-2 d-block fa-2x"></i>
                            No recent activity found
                        </td>
                    </tr>
                 `;
            } else {
                data.recent_activity.forEach(record => {
                    const row = document.createElement('tr');
                    
                    const statusBadge = record.status === 'PRESENT' 
                        ? '<span class="badge bg-success">Present</span>' 
                        : '<span class="badge bg-danger">Absent</span>';
                        
                    // Format date and time
                    const dateObj = new Date(record.lecture_date);
                    const formattedDate = dateObj.toLocaleDateString();
                    
                    row.innerHTML = `
                        <td class="ps-4 fw-bold">${record.subject || ''}</td>
                        <td>${formattedDate}</td>
                        <td>${statusBadge}</td>
                    `;
                    tbody.appendChild(row);
                });
            }
        }
    }

    // 3. Classes Today + Alerts
    const classesToday = document.getElementById('classesTodayValue');
    if (classesToday) classesToday.textContent = data.classes_today ?? 0;

    const alertsCount = document.getElementById('attendanceAlertsValue');
    if (alertsCount) alertsCount.textContent = data.attendance_alerts_count ?? 0;

    // 4. Alerts list
    const alertsEl = document.getElementById('dashboardAlerts');
    if (alertsEl) {
        alertsEl.innerHTML = '';
        const alerts = Array.isArray(data.attendance_alerts) ? data.attendance_alerts : [];
        alerts.forEach((a) => {
            const div = document.createElement('div');
            div.className = 'alert alert-warning d-flex align-items-center shadow-sm';
            div.role = 'alert';
            div.innerHTML = `<i class="fas fa-exclamation-triangle me-2"></i><div>${escapeHtml(a?.message || '')}</div>`;
            alertsEl.appendChild(div);
        });
    }
}

function escapeHtml(str) {
    return String(str ?? '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#039;');
}
