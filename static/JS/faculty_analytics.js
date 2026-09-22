let facultyDistributionChart = null;
let facultyTrendChart = null;
let facultyOverallTrendChart = null;

document.addEventListener('DOMContentLoaded', () => {
    initFacultyAnalytics().catch((e) => console.error(e));
});

async function initFacultyAnalytics() {
    const lectureSelect = document.getElementById('facultyLectureSelect');
    const subjectSelect = document.getElementById('facultySubjectTrendSelect');
    const fromDateEl = document.getElementById('facultyTrendFromDate');
    const toDateEl = document.getElementById('facultyTrendToDate');

    const overallFromEl = document.getElementById('facultyOverallFromDate');
    const overallToEl = document.getElementById('facultyOverallToDate');
    const overallApplyBtn = document.getElementById('facultyOverallApplyBtn');

    const subjectApplyBtn = document.getElementById('facultyTrendApplyBtn');

    // Populate from existing faculty history endpoint
    try {
        const history = await apiGet('/api/faculty/attendance/history');
        const rows = Array.isArray(history) ? history : [];

        if (lectureSelect) {
            lectureSelect.innerHTML = '<option value="">Select lecture...</option>';
            for (const r of rows) {
                const id = r?.lecture_id;
                if (!id) continue;
                const date = r?.lecture_date || '';
                const subject = r?.subject || '';
                const opt = document.createElement('option');
                opt.value = String(id);
                opt.textContent = `${subject} • ${date} (Lecture #${id})`;
                lectureSelect.appendChild(opt);
            }
        }

        if (subjectSelect) {
            const subjects = Array.from(new Set(rows.map((r) => (r?.subject || '').trim()).filter(Boolean))).sort();
            subjectSelect.innerHTML = '<option value="">Select subject...</option>';
            for (const s of subjects) {
                const opt = document.createElement('option');
                opt.value = s;
                opt.textContent = s;
                subjectSelect.appendChild(opt);
            }
        }

        if (lectureSelect && lectureSelect.value) {
            await loadLectureDistribution(lectureSelect.value);
        }
        if (subjectSelect && subjectSelect.value) {
            await loadLectureTrend(subjectSelect.value);
        }

        // Load overall trend initially (unfiltered)
        await loadOverallTrend();
    } catch (e) {
        console.error('Failed to initialize faculty analytics', e);
    }

    lectureSelect?.addEventListener('change', async () => {
        const id = lectureSelect.value;
        if (!id) return;
        await loadLectureDistribution(id);
    });

    subjectSelect?.addEventListener('change', async () => {
        const subject = subjectSelect.value;
        if (!subject) return;
        await loadLectureTrend(subject);
    });

    subjectApplyBtn?.addEventListener('click', async () => {
        const subject = subjectSelect?.value;
        if (!subject) return;
        await loadLectureTrend(subject);
    });

    const onDateChange = async () => {
        const subject = subjectSelect?.value;
        if (!subject) return;
        await loadLectureTrend(subject);
    };
    fromDateEl?.addEventListener('change', onDateChange);
    toDateEl?.addEventListener('change', onDateChange);

    overallApplyBtn?.addEventListener('click', async () => {
        await loadOverallTrend();
    });

    const onOverallDateChange = async () => {
        await loadOverallTrend();
    };
    overallFromEl?.addEventListener('change', onOverallDateChange);
    overallToEl?.addEventListener('change', onOverallDateChange);
}

function pctBadgeColor(pct) {
    const p = Number(pct || 0);
    if (p >= 85) return { bg: 'bg-success', text: 'text-white' };
    if (p >= 75) return { bg: 'bg-warning', text: 'text-dark' };
    return { bg: 'bg-danger', text: 'text-white' };
}

async function loadLectureDistribution(lectureId) {
    const badge = document.getElementById('facultyLecturePctBadge');
    try {
        const resp = await apiGet(`/api/faculty/lecture/stats?lecture_id=${encodeURIComponent(lectureId)}`);
        const present = Number(resp?.present ?? 0);
        const absent = Number(resp?.absent ?? 0);
        const pct = Number(resp?.percentage ?? 0);

        if (badge) {
            const cls = pctBadgeColor(pct);
            badge.className = `badge ${cls.bg} ${cls.text}`;
            badge.textContent = `${pct}%`;
        }

        const ctx = document.getElementById('facultyLectureDistributionChart');
        if (!ctx) return;

        if (facultyDistributionChart) facultyDistributionChart.destroy();
        facultyDistributionChart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: ['Present', 'Absent'],
                datasets: [{
                    data: [present, absent],
                    backgroundColor: ['rgba(25,135,84,0.8)', 'rgba(220,53,69,0.8)'],
                    borderWidth: 0,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom' },
                    tooltip: { enabled: true },
                }
            }
        });
    } catch (e) {
        console.error('Failed to load lecture distribution', e);
        if (badge) {
            badge.className = 'badge bg-secondary';
            badge.textContent = '—';
        }
    }
}

async function loadLectureTrend(subject) {
    const changeEl = document.getElementById('facultyTrendChangeText');
    try {
        const fromDate = (document.getElementById('facultyTrendFromDate')?.value || '').trim();
        const toDate = (document.getElementById('facultyTrendToDate')?.value || '').trim();

        const params = new URLSearchParams();
        params.set('subject', String(subject));
        if (fromDate) params.set('from_date', fromDate);
        if (toDate) params.set('to_date', toDate);

        const resp = await apiGet(`/api/faculty/lecture/trend?${params.toString()}`);
        const dates = Array.isArray(resp?.dates) ? resp.dates : [];
        const values = Array.isArray(resp?.attendance_percentages) ? resp.attendance_percentages : [];

        // Show change from previous lecture
        if (changeEl) {
            const n = values.length;
            if (n >= 2) {
                const diff = Number(values[n - 1]) - Number(values[n - 2]);
                const sign = diff > 0 ? '+' : '';
                changeEl.textContent = `${sign}${diff}% vs previous`;
                changeEl.className = diff >= 0 ? 'text-success small' : 'text-danger small';
            } else {
                changeEl.textContent = '—';
                changeEl.className = 'text-muted small';
            }
        }

        const ctx = document.getElementById('facultyLectureTrendChart');
        if (!ctx) return;

        if (facultyTrendChart) facultyTrendChart.destroy();
        facultyTrendChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: dates,
                datasets: [{
                    label: 'Attendance %',
                    data: values,
                    borderColor: 'rgba(13,110,253,1)',
                    backgroundColor: 'rgba(13,110,253,0.1)',
                    tension: 0.25,
                    fill: true,
                    pointRadius: 4,
                    pointHoverRadius: 6,
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
        console.error('Failed to load lecture trend', e);
        if (changeEl) {
            changeEl.textContent = '—';
            changeEl.className = 'text-muted small';
        }
    }
}

function setOverallAvgBadge(avgPct, riskLevel) {
    const badge = document.getElementById('facultyOverallAvgText');
    if (!badge) return;
    const pct = Number(avgPct ?? 0);
    const level = String(riskLevel || '—');

    badge.textContent = `${pct}% • ${level}`;
    badge.className = 'badge';
    if (level === 'SAFE') badge.classList.add('bg-success');
    else if (level === 'WARNING') badge.classList.add('bg-warning', 'text-dark');
    else if (level === 'CRITICAL') badge.classList.add('bg-danger');
    else badge.classList.add('bg-secondary');
}

async function loadOverallTrend() {
    try {
        const fromDate = (document.getElementById('facultyOverallFromDate')?.value || '').trim();
        const toDate = (document.getElementById('facultyOverallToDate')?.value || '').trim();

        const params = new URLSearchParams();
        if (fromDate) params.set('from_date', fromDate);
        if (toDate) params.set('to_date', toDate);

        const url = params.toString()
            ? `/api/faculty/analytics/overall-trend?${params.toString()}`
            : '/api/faculty/analytics/overall-trend';

        const resp = await apiGet(url);
        const dates = Array.isArray(resp?.dates) ? resp.dates : [];
        const values = Array.isArray(resp?.attendance_percentages) ? resp.attendance_percentages : [];

        setOverallAvgBadge(resp?.average_percentage, resp?.risk_level);

        const ctx = document.getElementById('facultyOverallTrendChart');
        if (!ctx) return;

        if (facultyOverallTrendChart) facultyOverallTrendChart.destroy();
        facultyOverallTrendChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: dates,
                datasets: [{
                    label: 'Attendance %',
                    data: values,
                    borderColor: 'rgba(108,117,125,1)',
                    backgroundColor: 'rgba(108,117,125,0.1)',
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
        console.error('Failed to load overall trend', e);
        setOverallAvgBadge(0, '—');
    }
}
