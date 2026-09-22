document.addEventListener('DOMContentLoaded', function() {
    loadFaculty();

    function notify(type, message, title) {
        if (typeof window.showToast === 'function') {
            window.showToast({ type, title: title || undefined, message });
        } else {
            console.warn(`[${type}] ${title ? title + ': ' : ''}${message}`);
        }
    }

    // Search / filter
    const facultySearchInput = document.getElementById('facultySearchInput');
    if (facultySearchInput) {
        facultySearchInput.addEventListener('input', function() {
            applyFacultyFilter();
        });
    }
    
    // Logout Logic
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async function() {
            try {
                await apiPostJson('/api/auth/logout', {});
                window.location.href = '/admin/login';
            } catch (error) {
                console.error('Logout error:', error);
                window.location.href = '/admin/login'; 
            }
        });
    }

    // Form Submission
    const form = document.getElementById('addFacultyForm');
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();

            const facultyIdEl = document.getElementById('facultyId');
            const isEdit = facultyIdEl && facultyIdEl.value;
            
            // Basic Validation
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
                form.classList.add('was-validated');
                return;
            }

            const name = document.getElementById('facultyName').value;
            const email = document.getElementById('facultyEmail').value;
            const password = document.getElementById('facultyPassword').value;
            const department = document.getElementById('department').value;
            
            // Additional Validation
            if (!isEdit) {
                if (password.length < 6) {
                    notify('warning', 'Password must be at least 6 characters long.', 'Validation');
                    return;
                }
            } else if (password && password.length < 6) {
                notify('warning', 'Password must be at least 6 characters long.', 'Validation');
                return;
            }

            const payload = {
                faculty_id: isEdit ? parseInt(facultyIdEl.value) : undefined,
                name: name,
                email: email,
                password: password || undefined,
                department: department
            };

            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Creating...';

            try {
                if (isEdit) {
                    await apiPostJson('/api/admin/faculty/update', payload);
                } else {
                    await apiPostJson('/api/admin/faculty/create', payload);
                }

                const modalEl = document.getElementById('addFacultyModal');
                const modal = bootstrap.Modal.getInstance(modalEl);
                if (modal) modal.hide();

                form.reset();
                form.classList.remove('was-validated');

                if (facultyIdEl) facultyIdEl.value = '';
                resetFacultyFormMode();

                notify('success', isEdit ? 'Faculty updated successfully!' : 'Faculty created successfully!', 'Success');
                loadFaculty(); // Refresh table
            } catch (error) {
                console.error('Error:', error);
                notify('error', getApiErrorMessage(error, isEdit ? 'Failed to update faculty' : 'Failed to create faculty'), 'Error');
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            }
        });
    }

    // Row actions (edit/status)
    const tbody = document.getElementById('facultyTableBody');
    if (tbody) {
        tbody.addEventListener('click', async function(e) {
            const editBtn = e.target.closest('.js-edit-faculty');
            const statusBtn = e.target.closest('.js-toggle-faculty-status, .js-delete-faculty');

            if (editBtn) {
                const id = parseInt(editBtn.dataset.id);
                const faculty = (window.__facultyListAll || []).find(f => f.faculty_id === id);
                if (!faculty) return;
                openFacultyEditModal(faculty);
            }

            if (statusBtn) {
                const id = parseInt(statusBtn.dataset.id);
                const faculty = (window.__facultyListAll || []).find(f => f.faculty_id === id);
                if (!faculty) return;

                const newStatus = !Boolean(faculty.is_active);
                const action = newStatus ? 'Activate' : 'Deactivate';
                if (typeof window.glassConfirm === 'function') {
                    const ok = await window.glassConfirm({
                        type: newStatus ? 'warning' : 'danger',
                        title: `${action} Faculty`,
                        message: `${action} this faculty account?`,
                        confirmText: action,
                        cancelText: 'Cancel'
                    });
                    if (!ok) return;
                }

                try {
                    await apiPostJson('/api/admin/faculty/status', { faculty_id: id, is_active: newStatus });
                    loadFaculty();
                } catch (error) {
                    console.error('Error:', error);
                    notify('error', getApiErrorMessage(error, `Failed to ${action.toLowerCase()} faculty`), 'Error');
                }
            }
        });
    }
});

async function loadFaculty() {
    try {
        const facultyList = await apiGet('/api/admin/faculty/list');
        window.__facultyListAll = Array.isArray(facultyList) ? facultyList : [];
        applyFacultyFilter();
    } catch (error) {
        console.error('Failed to load faculty:', error);
    }
}

function applyFacultyFilter() {
    const input = document.getElementById('facultySearchInput');
    const query = (input ? input.value : '').trim().toLowerCase();

    const list = Array.isArray(window.__facultyListAll) ? window.__facultyListAll : [];
    if (!query) {
        renderFacultyTable(list);
        return;
    }

    const filtered = list.filter(faculty => {
        const statusText = faculty.is_active ? 'active' : 'inactive';
        const haystack = [
            faculty.name,
            faculty.email,
            faculty.department,
            statusText,
            String(faculty.faculty_id ?? '')
        ]
            .filter(Boolean)
            .join(' ')
            .toLowerCase();
        return haystack.includes(query);
    });

    renderFacultyTable(filtered);
}

function renderFacultyTable(facultyList) {
    const tbody = document.getElementById('facultyTableBody');
    if (!tbody) return;

    tbody.innerHTML = '';
    if (!Array.isArray(facultyList) || facultyList.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center py-4 text-muted">No matching faculty found.</td></tr>';
        return;
    }

    facultyList.forEach(faculty => {
        const row = document.createElement('tr');
        const initials = (faculty.name || '')
            .split(' ')
            .filter(Boolean)
            .map(n => n[0])
            .join('')
            .substring(0, 2)
            .toUpperCase();

        row.innerHTML = `
            <td class="ps-4">
                <div class="d-flex align-items-center">
                    <div class="avatar-circle bg-primary text-white me-2" style="width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.9rem; font-weight: bold;">${initials || '?'}</div>
                    <div class="fw-semibold">${faculty.name || ''}</div>
                </div>
            </td>
            <td>${faculty.department || ''}</td>
            <td class="text-muted small">${faculty.email || ''}</td>
            <td>
                <span class="badge ${faculty.is_active ? 'bg-success-subtle text-success' : 'bg-danger-subtle text-danger'}">
                    ${faculty.is_active ? 'Active' : 'Inactive'}
                </span>
            </td>
            <td class="text-end pe-4">
                <button type="button" class="btn btn-sm btn-light text-primary js-edit-faculty" data-id="${faculty.faculty_id}" title="Edit"><i class="fas fa-edit"></i></button>
                <button type="button" class="btn btn-sm btn-light ${faculty.is_active ? 'text-danger' : 'text-success'} js-toggle-faculty-status" data-id="${faculty.faculty_id}" title="${faculty.is_active ? 'Deactivate' : 'Activate'}">
                    <i class="fas ${faculty.is_active ? 'fa-user-slash' : 'fa-user-check'}"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function openFacultyEditModal(faculty) {
    const modalEl = document.getElementById('addFacultyModal');
    const form = document.getElementById('addFacultyForm');
    if (!modalEl || !form) return;

    const titleEl = modalEl.querySelector('.modal-title');
    if (titleEl) titleEl.innerHTML = '<i class="fas fa-user-tie me-2"></i>Edit Faculty';

    document.getElementById('facultyId').value = faculty.faculty_id;
    document.getElementById('facultyName').value = faculty.name || '';
    document.getElementById('facultyEmail').value = faculty.email || '';
    document.getElementById('department').value = faculty.department || '';

    const pw = document.getElementById('facultyPassword');
    if (pw) {
        pw.value = '';
        pw.placeholder = 'Leave blank to keep unchanged';
        pw.removeAttribute('required');
    }

    // Button label
    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) submitBtn.innerHTML = '<i class="fas fa-save me-2"></i>Save Changes';

    form.classList.remove('was-validated');
    const modal = new bootstrap.Modal(modalEl);
    modal.show();
}

function resetFacultyFormMode() {
    const modalEl = document.getElementById('addFacultyModal');
    const form = document.getElementById('addFacultyForm');
    if (!modalEl || !form) return;

    const titleEl = modalEl.querySelector('.modal-title');
    if (titleEl) titleEl.innerHTML = '<i class="fas fa-user-tie me-2"></i>Add New Faculty';

    const pw = document.getElementById('facultyPassword');
    if (pw) {
        pw.value = '';
        pw.placeholder = 'Initial password for account';
        pw.setAttribute('required', 'required');
    }

    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) submitBtn.innerHTML = '<i class="fas fa-save me-2"></i>Create Account';
}
