let allReports = [];

document.addEventListener('DOMContentLoaded', async function() {
    const form = document.getElementById('reportFilterForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            applyFiltersAndRender();
        });
    }

    await fetchReports();
});

async function fetchReports() {
    try {
        const reportsBody = document.querySelector('tbody'); // We might need a specific ID to be safe
        const reports = await apiGet('/api/admin/reports/list');
        allReports = Array.isArray(reports) ? reports : [];
            
            if (reportsBody) {
                reportsBody.innerHTML = ''; // Clear hardcoded/placeholder rows
                
                if (reports.length === 0) {
                     reportsBody.innerHTML = `
                        <tr>
                            <td colspan="5" class="text-center py-4 text-muted">
                                <i class="fas fa-folder-open mb-2 fs-4 d-block"></i>
                                No reports generated yet
                            </td>
                        </tr>
                     `;
                     return;
                }

                allReports.forEach(report => {
                    const row = document.createElement('tr');
                    
                    // Format Date
                    const dateObj = new Date(report.created_at);
                    const formattedDate = dateObj.toLocaleDateString('en-US', { day: 'numeric', month: 'short', year: 'numeric' });
                    
                    // Determine Icon
                    let iconClass = 'fa-file-alt text-secondary';
                    if (report.report_type.toLowerCase().includes('attendance')) iconClass = 'fa-user-check text-success';
                    else if (report.report_type.toLowerCase().includes('finance') || report.report_type.toLowerCase().includes('subscription')) iconClass = 'fa-chart-line text-primary';
                    else if (report.report_type.toLowerCase().includes('system')) iconClass = 'fa-server text-warning';

                    row.innerHTML = `
                        <td class="ps-4">
                            <div class="d-flex align-items-center">
                                <i class="fas ${iconClass} me-3 fs-5"></i>
                                <div>
                                    <div class="fw-bold">${report.report_type}</div>
                                    <small class="text-muted">${report.generated_by}</small>
                                </div>
                            </div>
                        </td>
                        <td>${report.generated_by}</td>
                        <td><span class="badge bg-light text-dark border">${report.coverage_period || 'N/A'}</span></td>
                        <td class="text-muted small">${formattedDate}</td>
                        <td class="text-end pe-4">
                            <div class="dropdown">
                                <button class="btn btn-sm btn-link text-muted" type="button" data-bs-toggle="dropdown">
                                    <i class="fas fa-ellipsis-v"></i>
                                </button>
                                <ul class="dropdown-menu dropdown-menu-end">
                                    <li><a class="dropdown-item" href="#"><i class="fas fa-eye me-2"></i>View Details</a></li>
                                    <li><a class="dropdown-item" href="#"><i class="fas fa-download me-2"></i>Download PDF</a></li>
                                    <li><hr class="dropdown-divider"></li>
                                    <li><a class="dropdown-item text-danger" href="#"><i class="fas fa-trash-alt me-2"></i>Delete</a></li>
                                </ul>
                            </div>
                        </td>
                    `;
                    reportsBody.appendChild(row);
                });
            }
    } catch (error) {
        console.error('Network Error:', error);
        const reportsBody = document.querySelector('tbody');
        if (reportsBody) {
            reportsBody.innerHTML = `<tr><td colspan="5" class="text-center text-danger">${getApiErrorMessage(error, 'Failed to load reports')}</td></tr>`;
        }
    }
}

function applyFiltersAndRender() {
    const form = document.getElementById('reportFilterForm');
    if (!form || !allReports) return;

    // Clear errors
    document.querySelectorAll('.error-msg').forEach(el => el.textContent = '');
    document.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));

    const dept = document.getElementById('deptSelect');
    const start = document.getElementById('startDate');
    const end = document.getElementById('endDate');

    let isValid = true;
    if (dept && !dept.value) {
        showError(dept, 'deptError', 'Please select a department');
        isValid = false;
    }
    if (start && !start.value) {
        showError(start, 'startError', 'Start date required');
        isValid = false;
    }
    if (end && !end.value) {
        showError(end, 'endError', 'End date required');
        isValid = false;
    }
    if (start && end && start.value && end.value && start.value > end.value) {
        showError(end, 'endError', 'End date cannot be before start date');
        isValid = false;
    }
    if (!isValid) return;

    const deptValue = (dept && dept.value) ? dept.value.trim().toLowerCase() : '';
    const startDate = start && start.value ? new Date(start.value + 'T00:00:00') : null;
    const endDate = end && end.value ? new Date(end.value + 'T23:59:59') : null;

    const filtered = allReports.filter(r => {
        // Date filter (created_at)
        if (startDate || endDate) {
            const created = r.created_at ? new Date(r.created_at) : null;
            if (!created || isNaN(created.getTime())) return false;
            if (startDate && created < startDate) return false;
            if (endDate && created > endDate) return false;
        }

        // Dept filter: best-effort match against report_type/coverage_period strings
        if (deptValue) {
            const hay = `${r.report_type || ''} ${r.coverage_period || ''}`.toLowerCase();
            if (!hay.includes(deptValue)) return false;
        }
        return true;
    });

    renderReports(filtered);
}

function renderReports(reports) {
    const reportsBody = document.querySelector('tbody');
    if (!reportsBody) return;

    reportsBody.innerHTML = '';
    if (!reports || reports.length === 0) {
        reportsBody.innerHTML = `
            <tr>
                <td colspan="5" class="text-center py-4 text-muted">
                    <i class="fas fa-folder-open mb-2 fs-4 d-block"></i>
                    No reports match your filters
                </td>
            </tr>
        `;
        return;
    }

    reports.forEach(report => {
        const row = document.createElement('tr');
        const dateObj = new Date(report.created_at);
        const formattedDate = isNaN(dateObj.getTime())
            ? 'N/A'
            : dateObj.toLocaleDateString('en-US', { day: 'numeric', month: 'short', year: 'numeric' });

        let iconClass = 'fa-file-alt text-secondary';
        if ((report.report_type || '').toLowerCase().includes('attendance')) iconClass = 'fa-user-check text-success';
        else if ((report.report_type || '').toLowerCase().includes('finance') || (report.report_type || '').toLowerCase().includes('subscription')) iconClass = 'fa-chart-line text-primary';
        else if ((report.report_type || '').toLowerCase().includes('system')) iconClass = 'fa-server text-warning';

        row.innerHTML = `
            <td class="ps-4">
                <div class="d-flex align-items-center">
                    <i class="fas ${iconClass} me-3 fs-5"></i>
                    <div>
                        <div class="fw-bold">${report.report_type}</div>
                        <small class="text-muted">${report.generated_by}</small>
                    </div>
                </div>
            </td>
            <td>${report.generated_by}</td>
            <td><span class="badge bg-light text-dark border">${report.coverage_period || 'N/A'}</span></td>
            <td class="text-muted small">${formattedDate}</td>
            <td class="text-end pe-4">
                <div class="dropdown">
                    <button class="btn btn-sm btn-link text-muted" type="button" data-bs-toggle="dropdown">
                        <i class="fas fa-ellipsis-v"></i>
                    </button>
                    <ul class="dropdown-menu dropdown-menu-end">
                        <li><a class="dropdown-item" href="#"><i class="fas fa-eye me-2"></i>View Details</a></li>
                        <li><a class="dropdown-item" href="#"><i class="fas fa-download me-2"></i>Download PDF</a></li>
                    </ul>
                </div>
            </td>
        `;
        reportsBody.appendChild(row);
    });
}

function showError(input, errorId, msg) {
    input.classList.add('is-invalid');
    const el = document.getElementById(errorId);
    if (el) el.textContent = msg;
}
