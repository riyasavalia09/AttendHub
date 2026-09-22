document.addEventListener('DOMContentLoaded', async function() {
    // 1. Fetch Dashboard Stats
    try {
        const data = await apiGet('/api/admin/dashboard/summary');
            
            // --- Update Counters ---
            const facultyEl = document.getElementById('totalFacultyCount');
            if (facultyEl) facultyEl.textContent = data.total_faculty;
            
            const studentEl = document.getElementById('totalStudentCount');
            if (studentEl) studentEl.textContent = data.total_students;
            
            const timetableEl = document.getElementById('activeTimetableCount');
            if (timetableEl) timetableEl.textContent = data.active_timetables;
            
            const lectureEl = document.getElementById('lecturesTodayCount');
            if (lectureEl) lectureEl.textContent = data.today_lectures;

            // --- Update Recent Activity Table ---
            const activityBody = document.getElementById('recentActivityTableBody');
            if (activityBody) {
                // Clear existing/dummy rows
                activityBody.innerHTML = '';

                if (!data.recent_activity || data.recent_activity.length === 0) {
                     const row = document.createElement('tr');
                     row.innerHTML = `<td colspan="4" class="text-center text-muted p-3">No recent system activity found</td>`;
                     activityBody.appendChild(row);
                } else {
                    data.recent_activity.forEach(activity => {
                        const row = document.createElement('tr');
                        
                        // Determine badge color based on role
                        let badgeClass = 'bg-secondary';
                        let roleText = activity.role || 'Unknown';
                        
                        if (roleText.toLowerCase() === 'admin') badgeClass = 'bg-danger';
                        else if (roleText.toLowerCase() === 'faculty') badgeClass = 'bg-primary';
                        else if (roleText.toLowerCase() === 'student') badgeClass = 'bg-success';

                        // Format event text if helpful, otherwise raw string
                        const eventText = activity.event || 'System Action';
                        const userText = activity.user || 'System';
                        const timeText = activity.time || 'Just now';

                        row.innerHTML = `
                            <td class="ps-4 fw-medium">${eventText}</td>
                            <td>${userText}</td>
                            <td><span class="badge ${badgeClass}">${roleText}</span></td>
                            <td class="text-muted small">${timeText}</td>
                        `;
                        activityBody.appendChild(row);
                    });
                }
            }
    } catch (error) {
        console.error('Network Error:', error);
    }
});
