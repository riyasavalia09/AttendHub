let editModalInstance = null;
let facultyOptionsLoaded = false;

document.addEventListener('DOMContentLoaded', function () {
    loadTimetable();
    loadFacultyOptions();
    wireLogout();
    wireUpload();
    wireEditActions();
    wireSaveTimetable();
});

function wireLogout() {
    const logoutBtn = document.getElementById('logoutBtn');
    if (!logoutBtn) return;

    logoutBtn.addEventListener('click', async function () {
        try {
            await apiPostJson('/api/auth/logout', {});
            window.location.href = '/admin/login';
        } catch (error) {
            console.error('Logout error:', error);
            window.location.href = '/admin/login';
        }
    });
}

function wireUpload() {
    const uploadBtn = document.getElementById('uploadBtn');
    if (!uploadBtn) return;

    uploadBtn.addEventListener('click', async function () {
        const fileInput = document.getElementById('timetableInput');
        const errorDiv = document.getElementById('uploadError');
        errorDiv.style.display = 'none';
        errorDiv.textContent = '';

        if (!fileInput || fileInput.files.length === 0) {
            errorDiv.textContent = 'Please select a CSV file first.';
            errorDiv.style.display = 'block';
            return;
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        const originalText = uploadBtn.innerHTML;
        uploadBtn.disabled = true;
        uploadBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Uploading...';

        try {
            const result = await apiPostForm('/api/admin/timetable/upload', formData);
            const successCount = result && typeof result.success_count === 'number' ? result.success_count : 0;
            const errors = result && Array.isArray(result.errors) ? result.errors : [];

            if (errors.length > 0) {
                errorDiv.innerHTML = `Imported ${successCount} rows. ${errors.length} error(s):<br>` +
                    errors.slice(0, 6).map((e) => `- ${escapeHtml(e)}`).join('<br>') +
                    (errors.length > 6 ? '<br>- ...' : '');
                errorDiv.style.display = 'block';
            }

            if (successCount > 0) {
                if (typeof window.showToast === 'function') {
                    window.showToast({
                        type: 'success',
                        title: 'Imported',
                        message: `Timetable imported: ${successCount} row(s).`
                    });
                }
                fileInput.value = '';
                await loadTimetable();
            }
        } catch (error) {
            console.error('Upload error:', error);
            errorDiv.textContent = getApiErrorMessage(error, 'Upload failed.');
            errorDiv.style.display = 'block';
        } finally {
            uploadBtn.disabled = false;
            uploadBtn.innerHTML = originalText;
        }
    });
}

function wireEditActions() {
    const tbody = document.getElementById('timetableTableBody');
    if (!tbody) return;

    tbody.addEventListener('click', async (event) => {
        const btn = event.target.closest('.edit-btn');
        if (!btn) return;

        const timetableId = parseInt(btn.getAttribute('data-id'), 10);
        if (!timetableId) return;

        await openEditModal(timetableId);
    });
}

function wireSaveTimetable() {
    const saveBtn = document.getElementById('saveTimetableBtn');
    if (!saveBtn) return;

    saveBtn.addEventListener('click', async () => {
        const timetableId = parseInt(document.getElementById('editTimetableId')?.value || '', 10);
        const errorEl = document.getElementById('editTimetableError');
        if (errorEl) {
            errorEl.textContent = '';
            errorEl.classList.add('d-none');
        }

        if (!timetableId) {
            showEditError('Invalid timetable id');
            return;
        }

        const payload = {
            subject: document.getElementById('editSubject')?.value?.trim(),
            faculty_id: parseInt(document.getElementById('editFacultyId')?.value || '', 10),
            day: document.getElementById('editDay')?.value,
            start_time: document.getElementById('editStartTime')?.value,
            end_time: document.getElementById('editEndTime')?.value,
            department: document.getElementById('editDepartment')?.value?.trim(),
            semester: parseInt(document.getElementById('editSemester')?.value || '', 10),
        };

        const originalText = saveBtn.innerHTML;
        saveBtn.disabled = true;
        saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Saving...';

        try {
            await apiRequest(`/api/admin/timetable/${encodeURIComponent(String(timetableId))}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });

            if (typeof window.showToast === 'function') {
                window.showToast({
                    type: 'success',
                    title: 'Updated',
                    message: 'Timetable updated successfully'
                });
            }

            if (editModalInstance) editModalInstance.hide();
            await loadTimetable();
        } catch (error) {
            showEditError(getApiErrorMessage(error, 'Failed to update timetable'));
        } finally {
            saveBtn.disabled = false;
            saveBtn.innerHTML = originalText;
        }
    });
}

function showEditError(message) {
    const errorEl = document.getElementById('editTimetableError');
    if (!errorEl) return;
    errorEl.textContent = message || 'Validation failed';
    errorEl.classList.remove('d-none');
}

async function loadFacultyOptions() {
    if (facultyOptionsLoaded) return;

    const select = document.getElementById('editFacultyId');
    if (!select) return;

    try {
        const list = await apiGet('/api/admin/faculty/list');
        const rows = Array.isArray(list) ? list : [];
        select.innerHTML = '<option value="">Select Faculty</option>' + rows.map((f) => {
            const id = f?.faculty_id;
            const name = f?.name || '';
            const dept = f?.department || '';
            return `<option value="${escapeHtml(id)}">${escapeHtml(name)}${dept ? ' (' + escapeHtml(dept) + ')' : ''}</option>`;
        }).join('');
        facultyOptionsLoaded = true;
    } catch (error) {
        console.error('Failed to load faculty list', error);
    }
}

function normalizeTimeForInput(value) {
    if (!value) return '';
    const text = String(value);
    return text.length >= 5 ? text.substring(0, 5) : text;
}

async function openEditModal(timetableId) {
    await loadFacultyOptions();
    const saveBtn = document.getElementById('saveTimetableBtn');
    if (saveBtn) saveBtn.disabled = false;

    const errorEl = document.getElementById('editTimetableError');
    if (errorEl) {
        errorEl.textContent = '';
        errorEl.classList.add('d-none');
    }

    try {
        const row = await apiGet(`/api/admin/timetable/${encodeURIComponent(String(timetableId))}`);
        document.getElementById('editTimetableId').value = row?.timetable_id || timetableId;
        document.getElementById('editSubject').value = row?.subject || '';
        document.getElementById('editFacultyId').value = row?.faculty_id != null ? String(row.faculty_id) : '';
        document.getElementById('editDay').value = (row?.day || 'MON').toUpperCase();
        document.getElementById('editStartTime').value = normalizeTimeForInput(row?.start_time);
        document.getElementById('editEndTime').value = normalizeTimeForInput(row?.end_time);
        document.getElementById('editDepartment').value = row?.department || '';
        document.getElementById('editSemester').value = row?.semester != null ? String(row.semester) : '';

        if (row?.has_lectures) {
            showEditError('This timetable entry is locked because lecture records already exist.');
            if (saveBtn) saveBtn.disabled = true;
        }

        const modalEl = document.getElementById('editTimetableModal');
        if (!modalEl) return;
        editModalInstance = window.bootstrap?.Modal?.getOrCreateInstance(modalEl);
        editModalInstance?.show();
    } catch (error) {
        const msg = getApiErrorMessage(error, 'Failed to load timetable detail');
        if (typeof window.showToast === 'function') {
            window.showToast({
                type: 'error',
                title: 'Error',
                message: msg
            });
        } else {
            window.alert(msg);
        }
    }
}

async function loadTimetable() {
    try {
        const timetableData = await apiGet('/api/admin/timetable/list');
        const tbody = document.getElementById('timetableTableBody');
        if (!tbody) return;
        tbody.innerHTML = '';

        if (!Array.isArray(timetableData) || timetableData.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center py-4 text-muted">No schedule available. Upload a CSV to get started.</td></tr>';
            return;
        }

        timetableData.forEach((item) => {
            const row = document.createElement('tr');
            const startTime = item.start_time ? String(item.start_time).substring(0, 5) : '';
            const endTime = item.end_time ? String(item.end_time).substring(0, 5) : '';
            const hasLectures = !!item.has_lectures;
            const actionBtnClass = 'btn btn-sm btn-outline-secondary edit-btn';
            const actionBtn = hasLectures
                ? `<button class="${actionBtnClass}" style="min-width:84px;" data-id="${item.timetable_id}" data-locked="1" title="Locked: lectures already exist">Edit</button>`
                : `<button class="${actionBtnClass}" style="min-width:84px;" data-id="${item.timetable_id}" data-locked="0">Edit</button>`;

            row.innerHTML = `
                <td class="ps-4 text-start fw-bold text-muted">${escapeHtml(item.department || '-')}</td>
                <td>${item.semester ? `${escapeHtml(item.semester)}th Sem` : '-'}</td>
                <td>${escapeHtml(item.day || '-')}</td>
                <td>${escapeHtml(startTime)} - ${escapeHtml(endTime)}</td>
                <td>
                    <div class="fw-bold">${escapeHtml(item.subject || '')}</div>
                    <div class="small text-muted">${escapeHtml(item.faculty_name || '')}</div>
                </td>
                <td class="text-end pe-4">${actionBtn}</td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Failed to load timetable:', error);
        const tbody = document.getElementById('timetableTableBody');
        if (tbody) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center py-4 text-danger">Failed to load schedule. Please refresh.</td></tr>';
        }
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
