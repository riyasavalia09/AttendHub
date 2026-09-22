let studentOverallChart = null;
let studentSubjectChart = null;

document.addEventListener('DOMContentLoaded', () => {
    loadStudentAttendanceCharts().catch((e) => console.error(e));
});

function subjectBarColor(pct) {
    const p = Number(pct || 0);
    if (p < 75) return 'rgba(220,53,69,0.8)';
    if (p < 85) return 'rgba(253,126,20,0.8)';
    return 'rgba(25,135,84,0.8)';
}

async function loadStudentAttendanceCharts() {
    try {
        const resp = await apiGet('/api/student/attendance/chart');
        const subjects = Array.isArray(resp?.subjects) ? resp.subjects : [];
        const percentages = Array.isArray(resp?.percentages) ? resp.percentages : [];
        const overall = Number(resp?.overall ?? 0);

        // Donut overall
        const donut = document.getElementById('studentOverallAttendanceChart');
        if (donut) {
            const overallColor = subjectBarColor(overall);
            if (studentOverallChart) studentOverallChart.destroy();
            studentOverallChart = new Chart(donut, {
                type: 'doughnut',
                data: {
                    labels: ['Overall %', 'Remaining %'],
                    datasets: [{
                        data: [overall, Math.max(0, 100 - overall)],
                        backgroundColor: [overallColor, 'rgba(108,117,125,0.2)'],
                        borderWidth: 0,
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '70%',
                    plugins: {
                        legend: { position: 'bottom' },
                        tooltip: { enabled: true },
                    }
                }
            });
        }

        const overallText = document.getElementById('studentOverallPctText');
        if (overallText) overallText.textContent = `${overall}%`;

        // Bar per subject
        const bar = document.getElementById('studentSubjectAttendanceChart');
        if (bar) {
            const colors = percentages.map(subjectBarColor);
            if (studentSubjectChart) studentSubjectChart.destroy();
            studentSubjectChart = new Chart(bar, {
                type: 'bar',
                data: {
                    labels: subjects,
                    datasets: [{
                        label: 'Attendance %',
                        data: percentages,
                        backgroundColor: colors,
                        borderWidth: 0,
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: { enabled: true },
                    },
                    scales: {
                        y: { beginAtZero: true, max: 100, ticks: { callback: (v) => `${v}%` } },
                    }
                }
            });
        }

        const lowList = document.getElementById('studentLowSubjectsList');
        if (lowList) {
            lowList.innerHTML = '';
            const lows = subjects
                .map((s, i) => ({ subject: s, pct: Number(percentages[i] ?? 0) }))
                .filter((x) => x.pct < 75);

            if (lows.length === 0) {
                lowList.innerHTML = '<span class="text-muted small">No subjects below 75%.</span>';
            } else {
                for (const x of lows) {
                    const pill = document.createElement('span');
                    pill.className = 'badge bg-danger me-2 mb-2';
                    pill.textContent = `${x.subject}: ${x.pct}%`;
                    lowList.appendChild(pill);
                }
            }
        }

    } catch (e) {
        console.error('Failed to load student attendance chart', e);
    }
}
