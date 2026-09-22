document.addEventListener('DOMContentLoaded', async function() {
    try {
        const data = await apiGet('/api/student/attendance');
        
        // 1. Update Summary Cards
        // Check if elements exist before setting
        const overallEl = document.getElementById('overallPercentage');
        if(overallEl) overallEl.textContent = `${data.summary.overallPercentage}%`;

        const totalEl = document.getElementById('totalLectures');
        if(totalEl) totalEl.textContent = data.summary.totalLectures;

        const presentEl = document.getElementById('totalPresent');
        if(presentEl) presentEl.textContent = data.summary.totalPresent;

        const absentEl = document.getElementById('totalAbsent');
        if(absentEl) absentEl.textContent = data.summary.totalAbsent;
        
        // 2. Populate Table
        const tableBody = document.getElementById('attendanceTableBody');
        if (!tableBody) return;

        tableBody.innerHTML = ''; // Clear existing specific rows
        
        if (data.subjects.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="6" class="text-center p-4">No attendance records found</td></tr>';
            return;
        }

        data.subjects.forEach(subject => {
            const row = document.createElement('tr');
            
            // Badge Logic
            let badgeClass = 'bg-primary';
            if (subject.status === 'Good') badgeClass = 'bg-success';
            if (subject.status === 'Satisfactory') badgeClass = 'bg-primary'; // Kept primary for satisfactory as per original mock
            if (subject.status === 'Warning') badgeClass = 'bg-warning text-dark';
            if (subject.status === 'Critical') badgeClass = 'bg-danger';

            let progressBarClass = 'bg-primary';
            if (subject.percentage >= 85) progressBarClass = 'bg-success';
            else if (subject.percentage >= 75) progressBarClass = 'bg-primary';
            else if (subject.percentage >= 60) progressBarClass = 'bg-warning';
            else progressBarClass = 'bg-danger';

            row.innerHTML = `
                <td class="ps-4">
                    <div class="fw-bold">${subject.name}</div>
                    <small class="text-muted">${subject.code || '--'}</small>
                </td>
                <td class="text-center">${subject.total}</td>
                <td class="text-center fw-bold">${subject.present}</td>
                <td class="text-center text-danger">${subject.absent}</td>
                <td>
                    <div class="d-flex align-items-center">
                        <span class="me-2 fw-bold">${subject.percentage}%</span>
                        <div class="progress flex-grow-1" style="height: 8px;">
                            <div class="progress-bar ${progressBarClass}" role="progressbar" style="width: ${subject.percentage}%"></div>
                        </div>
                    </div>
                </td>
                <td><span class="badge ${badgeClass} rounded-pill px-3">${subject.status}</span></td>
            `;
            tableBody.appendChild(row);
        });
        
    } catch (error) {
        console.error('Error loading attendance:', error);
    }
});
