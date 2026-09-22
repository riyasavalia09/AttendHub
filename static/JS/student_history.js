document.addEventListener('DOMContentLoaded', async function() {
    try {
        const data = await apiGet('/api/student/attendance/history');
        
        const tableBody = document.getElementById('historyTableBody');
        const countLabel = document.getElementById('recordCount');
        
        tableBody.innerHTML = ''; // Clear loading
        
        if (data.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="5" class="text-center p-4">No attendance records found.</td></tr>';
            countLabel.textContent = 'Total Records: 0';
            return;
        }

        countLabel.textContent = `Total Records: ${data.length}`;

        data.forEach(record => {
            const row = document.createElement('tr');
            
            // Format Dates
            const lectureDate = new Date(record.lecture_date).toLocaleDateString(undefined, {
                year: 'numeric', month: 'short', day: 'numeric'
            });
            
            // Format Time (assuming HH:MM:SS or similar from DB)
            // Ideally backend sends ISO, but if string, display as is or parse
            const startTime = record.start_time; // e.g. "10:00:00"
            const endTime = record.end_time;
            
            // Marked At
            let markedAt = '--';
            if (record.marked_at) {
                markedAt = new Date(record.marked_at).toLocaleTimeString(undefined, {
                    hour: '2-digit', minute: '2-digit'
                });
            }

            // Status Badge
            let statusBadge = '<span class="badge bg-secondary">Unknown</span>';
            if (record.status === 'PRESENT') {
                statusBadge = '<span class="badge bg-success rounded-pill px-3"><i class="fas fa-check me-1"></i>Present</span>';
            } else if (record.status === 'ABSENT') {
                statusBadge = '<span class="badge bg-danger rounded-pill px-3"><i class="fas fa-times me-1"></i>Absent</span>';
            }

            row.innerHTML = `
                <td class="ps-4 fw-bold text-dark">${lectureDate}</td>
                <td>
                    <div class="fw-bold text-primary">${record.subject}</div>
                </td>
                <td>${startTime} - ${endTime}</td>
                <td>${statusBadge}</td>
                <td class="text-muted small">${markedAt}</td>
            `;
            tableBody.appendChild(row);
        });
        
    } catch (error) {
        console.error("Error:", error);
        document.getElementById('historyTableBody').innerHTML = 
            `<tr><td colspan="5" class="text-center text-danger p-4">${getApiErrorMessage(error, 'Error loading data. Please try again later.')}</td></tr>`;
    }
});
