let analysisOverallChart = null;
let analysisRadarChart = null;
let analysisRecentChart = null;
let analysisAllSubjects = [];

document.addEventListener('DOMContentLoaded', () => {
    initStudentAnalysis().catch((e) => console.error(e));
});

function riskLevelFromPct(pct) {
    const p = Number(pct || 0);
    if (p >= 85) return 'SAFE';
    if (p >= 75) return 'WARNING';
    return 'CRITICAL';
}

function riskColor(level) {
    if (level === 'SAFE') return '#198754';
    if (level === 'WARNING') return '#fd7e14';
    return '#dc3545';
}

function subjectRadarColor(pct) {
    const p = Number(pct || 0);
    if (p < 75) return 'rgba(220,53,69,0.7)';
    if (p < 85) return 'rgba(253,126,20,0.7)';
    return 'rgba(25,135,84,0.7)';
}

function setOverallBadge(overallPct) {
    const badge = document.getElementById('analysisOverallStatusBadge');
    const pctText = document.getElementById('analysisOverallPctText');
    if (pctText) pctText.textContent = `${Number(overallPct || 0)}%`;

    if (!badge) return;
    const level = riskLevelFromPct(overallPct);
    badge.textContent = level;
    badge.className = 'badge';
    badge.style.backgroundColor = riskColor(level);
    badge.style.color = '#fff';
}

function getFilters() {
    const subject = (document.getElementById('analysisSubjectFilter')?.value || '').trim();
    const fromDate = (document.getElementById('analysisFromDate')?.value || '').trim();
    const toDate = (document.getElementById('analysisToDate')?.value || '').trim();

    return {
        subject: subject || '',
        from_date: fromDate || '',
        to_date: toDate || '',
    };
}

async function initStudentAnalysis() {
    const applyBtn = document.getElementById('analysisApplyBtn');
    const resetBtn = document.getElementById('analysisResetBtn');

    // Initial load (unfiltered) - also used to populate subject dropdown.
    const [initial, initialRecent] = await Promise.all([
        fetchChartData({}),
        fetchRecentTrend({}),
    ]);
    analysisAllSubjects = Array.isArray(initial?.subjects) ? initial.subjects : [];
    populateSubjectFilter(analysisAllSubjects);
    renderCharts(initial, initialRecent);

    applyBtn?.addEventListener('click', async () => {
        const filters = getFilters();
        const [data, recent] = await Promise.all([
            fetchChartData(filters),
            fetchRecentTrend(filters),
        ]);
        renderCharts(data, recent);
    });

    resetBtn?.addEventListener('click', async () => {
        const subjectEl = document.getElementById('analysisSubjectFilter');
        const fromEl = document.getElementById('analysisFromDate');
        const toEl = document.getElementById('analysisToDate');
        if (subjectEl) subjectEl.value = '';
        if (fromEl) fromEl.value = '';
        if (toEl) toEl.value = '';

        const [data, recent] = await Promise.all([
            fetchChartData({}),
            fetchRecentTrend({}),
        ]);
        renderCharts(data, recent);
    });
}

function populateSubjectFilter(subjects) {
    const select = document.getElementById('analysisSubjectFilter');
    if (!select) return;

    select.innerHTML = '<option value="">All Subjects</option>';
    for (const s of subjects || []) {
        const opt = document.createElement('option');
        opt.value = s;
        opt.textContent = s;
        select.appendChild(opt);
    }
}

async function fetchChartData(filters) {
    const params = new URLSearchParams();
    if (filters?.subject) params.set('subject', filters.subject);
    if (filters?.from_date) params.set('from_date', filters.from_date);
    if (filters?.to_date) params.set('to_date', filters.to_date);

    const url = params.toString()
        ? `/api/student/attendance/chart?${params.toString()}`
        : '/api/student/attendance/chart';

    return await apiGet(url);
}

async function fetchRecentTrend(filters) {
    const params = new URLSearchParams();
    if (filters?.subject) params.set('subject', filters.subject);
    if (filters?.from_date) params.set('from_date', filters.from_date);
    if (filters?.to_date) params.set('to_date', filters.to_date);
    params.set('limit', '5');

    return await apiGet(`/api/student/attendance/recent-trend?${params.toString()}`);
}

function renderCharts(resp, recentResp) {
    const subjects = Array.isArray(resp?.subjects) ? resp.subjects : [];
    const percentages = Array.isArray(resp?.percentages) ? resp.percentages : [];
    const overall = Number(resp?.overall ?? 0);

    setOverallBadge(overall);

    const statusLine = document.getElementById('analysisFilterSummary');
    if (statusLine) {
        const f = getFilters();
        const parts = [];
        if (f.subject) parts.push(`Subject: ${f.subject}`);
        if (f.from_date) parts.push(`From: ${f.from_date}`);
        if (f.to_date) parts.push(`To: ${f.to_date}`);
        statusLine.textContent = parts.length ? parts.join(' • ') : 'Showing all data';
    }

    // Donut overall
    const donut = document.getElementById('analysisOverallDonutChart');
    if (donut) {
        const level = riskLevelFromPct(overall);
        const color = riskColor(level);
        if (analysisOverallChart) analysisOverallChart.destroy();
        analysisOverallChart = new Chart(donut, {
            type: 'doughnut',
            data: {
                labels: ['Overall %', 'Remaining %'],
                datasets: [{
                    data: [overall, Math.max(0, 100 - overall)],
                    backgroundColor: [color, 'rgba(108,117,125,0.2)'],
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

    // Radar subject performance
    const radar = document.getElementById('analysisSubjectRadarChart');
    if (radar) {
        const baseColor = 'rgba(13,110,253,0.25)';
        const borderColor = 'rgba(13,110,253,1)';
        const pointColors = percentages.map(subjectRadarColor);

        if (analysisRadarChart) analysisRadarChart.destroy();
        analysisRadarChart = new Chart(radar, {
            type: 'radar',
            data: {
                labels: subjects,
                datasets: [{
                    label: 'Attendance %',
                    data: percentages,
                    backgroundColor: baseColor,
                    borderColor,
                    pointBackgroundColor: pointColors,
                    pointRadius: 3,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'top' },
                    tooltip: { enabled: true },
                },
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100,
                        ticks: { callback: (v) => `${v}%` },
                    }
                }
            }
        });
    }

    // Recent trend mini line
    const recentDates = Array.isArray(recentResp?.dates) ? recentResp.dates : [];
    const recentValues = Array.isArray(recentResp?.attendance_percentages) ? recentResp.attendance_percentages : [];

    const avgText = document.getElementById('analysisRecentAvgText');
    if (avgText) {
        const avg = Number(recentResp?.average_percentage ?? 0);
        const lvl = String(recentResp?.risk_level || '—');
        avgText.textContent = recentDates.length ? `Avg: ${avg}% • ${lvl}` : 'No recent lectures in this range';
    }

    const recentCanvas = document.getElementById('analysisRecentTrendChart');
    if (recentCanvas) {
        if (analysisRecentChart) analysisRecentChart.destroy();
        analysisRecentChart = new Chart(recentCanvas, {
            type: 'line',
            data: {
                labels: recentDates,
                datasets: [{
                    label: 'Lecture Attendance',
                    data: recentValues,
                    borderColor: 'rgba(108,117,125,1)',
                    backgroundColor: 'rgba(108,117,125,0.1)',
                    tension: 0.2,
                    fill: false,
                    pointRadius: 4,
                    pointHoverRadius: 6,
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
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: { callback: (v) => `${v}%` },
                    },
                }
            }
        });
    }
}
