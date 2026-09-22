    let adminDepartmentAvgChart = null;
let adminUniversityTrendChart = null;
let adminLowestChart = null;

document.addEventListener('DOMContentLoaded', () => {
    initAdminAnalytics().catch((e) => console.error(e));
});

function riskColor(riskLevel) {
    if (riskLevel === 'SAFE') return '#198754';
    if (riskLevel === 'WARNING') return '#fd7e14';
    return '#dc3545';
}

function pctBarColor(pct) {
    const p = Number(pct || 0);
    if (p < 75) return 'rgba(220,53,69,0.85)';
    if (p < 85) return 'rgba(253,126,20,0.85)';
    return 'rgba(25,135,84,0.85)';
}

function setAvgBadge(avgPct, riskLevel) {
    const pctEl = document.getElementById('adminAvgPctText');
    const badge = document.getElementById('adminAvgRiskBadge');
    if (pctEl) pctEl.textContent = `${Number(avgPct ?? 0)}%`;
    if (!badge) return;

    const level = riskLevel || '—';
    badge.textContent = level;
    badge.className = 'badge';
    badge.style.backgroundColor = riskColor(level);
    badge.style.color = '#fff';
}

function getDateFilters() {
    const fromDate = (document.getElementById('adminFromDate')?.value || '').trim();
    const toDate = (document.getElementById('adminToDate')?.value || '').trim();
    return { from_date: fromDate || '', to_date: toDate || '' };
}

async function initAdminAnalytics() {
    const applyBtn = document.getElementById('adminApplyBtn');
    const resetBtn = document.getElementById('adminResetBtn');

    await loadAllAdminAnalytics();

    applyBtn?.addEventListener('click', async () => {
        await loadAllAdminAnalytics();
    });

    resetBtn?.addEventListener('click', async () => {
        const fromEl = document.getElementById('adminFromDate');
        const toEl = document.getElementById('adminToDate');
        if (fromEl) fromEl.value = '';
        if (toEl) toEl.value = '';
        await loadAllAdminAnalytics();
    });
}

async function loadAllAdminAnalytics() {
    const f = getDateFilters();
    await Promise.all([
        loadDepartmentAverages(f),
        loadUniversityTrend(f),
        loadLowestAttendance(f),
    ]);
}

async function loadDepartmentAverages(filters) {
    try {
        const params = new URLSearchParams();
        if (filters?.from_date) params.set('from_date', filters.from_date);
        if (filters?.to_date) params.set('to_date', filters.to_date);

        const url = params.toString()
            ? `/api/admin/analytics/departments-avg?${params.toString()}`
            : '/api/admin/analytics/departments-avg';

        const resp = await apiGet(url);
        const departments = Array.isArray(resp?.departments) ? resp.departments : [];
        const percentages = Array.isArray(resp?.percentages) ? resp.percentages : [];

        const ctx = document.getElementById('adminDepartmentAvgChart');
        if (!ctx) return;

        const colors = percentages.map(pctBarColor);
        if (adminDepartmentAvgChart) adminDepartmentAvgChart.destroy();
        adminDepartmentAvgChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: departments,
                datasets: [{
                    label: 'Avg Attendance %',
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
    } catch (e) {
        console.error('Failed to load department averages', e);
    }
}

async function loadUniversityTrend(filters) {
    try {
        const params = new URLSearchParams();
        if (filters?.from_date) params.set('from_date', filters.from_date);
        if (filters?.to_date) params.set('to_date', filters.to_date);

        const url = params.toString()
            ? `/api/admin/analytics/university-trend?${params.toString()}`
            : '/api/admin/analytics/university-trend';

        const resp = await apiGet(url);
        const dates = Array.isArray(resp?.dates) ? resp.dates : [];
        const values = Array.isArray(resp?.attendance_percentages) ? resp.attendance_percentages : [];

        setAvgBadge(resp?.average_percentage, resp?.risk_level);

        const ctx = document.getElementById('adminUniversityTrendChart');
        if (!ctx) return;

        if (adminUniversityTrendChart) adminUniversityTrendChart.destroy();
        adminUniversityTrendChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: dates,
                datasets: [{
                    label: 'Attendance %',
                    data: values,
                    borderColor: 'rgba(13,110,253,1)',
                    backgroundColor: 'rgba(13,110,253,0.1)',
                    tension: 0.25,
                    fill: false,
                    pointRadius: 3,
                    pointHoverRadius: 5,
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
                    y: { beginAtZero: true, max: 100, ticks: { callback: (v) => `${v}%` } },
                }
            }
        });
    } catch (e) {
        console.error('Failed to load university trend', e);
        setAvgBadge(0, '—');
    }
}

async function loadLowestAttendance(filters) {
    try {
        const params = new URLSearchParams();
        params.set('limit', '5');
        if (filters?.from_date) params.set('from_date', filters.from_date);
        if (filters?.to_date) params.set('to_date', filters.to_date);

        const resp = await apiGet(`/api/admin/attendance/lowest?${params.toString()}`);
        const students = Array.isArray(resp?.students) ? resp.students : [];
        const percentages = Array.isArray(resp?.percentages) ? resp.percentages : [];
        const colors = percentages.map(pctBarColor);

        const ctx = document.getElementById('adminLowestChart');
        if (!ctx) return;

        if (adminLowestChart) adminLowestChart.destroy();
        adminLowestChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: students,
                datasets: [{
                    label: 'Attendance %',
                    data: percentages,
                    backgroundColor: colors,
                    borderWidth: 0,
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: true },
                },
                scales: {
                    x: { beginAtZero: true, max: 100, ticks: { callback: (v) => `${v}%` } },
                    y: { ticks: { autoSkip: false } },
                }
            }
        });
    } catch (e) {
        console.error('Failed to load lowest attendance', e);
    }
}
