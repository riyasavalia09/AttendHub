document.addEventListener('DOMContentLoaded', function() {
    loadStudents();

    function notify(type, message, title) {
        if (typeof window.showToast === 'function') {
            window.showToast({ type, title: title || undefined, message });
        } else {
            console.warn(`[${type}] ${title ? title + ': ' : ''}${message}`);
        }
    }

    // Search / filter
    const studentSearchInput = document.getElementById('studentSearchInput');
    if (studentSearchInput) {
        studentSearchInput.addEventListener('input', function() {
            applyStudentFilter();
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
    const form = document.getElementById('addStudentForm');
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();

            const studentIdEl = document.getElementById('studentId');
            const isEdit = studentIdEl && studentIdEl.value;
            
            // Basic Validation
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
                form.classList.add('was-validated');
                return;
            }

            const name = document.getElementById('studentName').value;
            const enrollmentNo = document.getElementById('enrollmentNo').value;
            const email = document.getElementById('studentEmail').value;
            const department = document.getElementById('department').value;
            const semester = document.getElementById('semester') ? document.getElementById('semester').value : 1;
            const password = document.getElementById('studentPassword').value;

            if (!isEdit) {
                if (!password || password.length < 6) {
                    notify('warning', 'Password must be at least 6 characters', 'Validation');
                    return;
                }
            } else if (password && password.length < 6) {
                notify('warning', 'Password must be at least 6 characters', 'Validation');
                return;
            }

            const payload = {
                student_id: isEdit ? parseInt(studentIdEl.value) : undefined,
                name: name,
                enrollment_no: enrollmentNo,
                email: email,
                department: department,
                semester: parseInt(semester),
                password: password || undefined
            };

            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Registering...';

            try {
                if (isEdit) {
                    await apiPostJson('/api/admin/student/update', payload);
                } else {
                    await apiPostJson('/api/admin/student/create', payload);
                }

                const modalEl = document.getElementById('addStudentModal');
                const modal = bootstrap.Modal.getInstance(modalEl);
                if (modal) modal.hide();

                form.reset();
                form.classList.remove('was-validated');

                if (studentIdEl) studentIdEl.value = '';
                resetStudentFormMode();

                notify('success', isEdit ? 'Student updated successfully!' : 'Student registered successfully!', 'Success');
                loadStudents(); // Refresh table
            } catch (error) {
                console.error('Error:', error);
                notify('error', getApiErrorMessage(error, isEdit ? 'Failed to update student' : 'Failed to register student'), 'Error');
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            }
        });
    }

    // Row actions (edit/status)
    const tbody = document.getElementById('studentTableBody');
    if (tbody) {
        tbody.addEventListener('click', async function(e) {
            const editBtn = e.target.closest('.js-edit-student');
            const statusBtn = e.target.closest('.js-toggle-student-status, .js-delete-student');

            if (editBtn) {
                const id = parseInt(editBtn.dataset.id);
                const student = (window.__studentListAll || []).find(s => s.student_id === id);
                if (!student) return;
                openStudentEditModal(student);
            }

            if (statusBtn) {
                const id = parseInt(statusBtn.dataset.id);
                const student = (window.__studentListAll || []).find(s => s.student_id === id);
                if (!student) return;

                const newStatus = !Boolean(student.is_active);
                const action = newStatus ? 'Activate' : 'Deactivate';
                if (typeof window.glassConfirm === 'function') {
                    const ok = await window.glassConfirm({
                        type: newStatus ? 'warning' : 'danger',
                        title: `${action} Student`,
                        message: `${action} this student account?`,
                        confirmText: action,
                        cancelText: 'Cancel'
                    });
                    if (!ok) return;
                }

                try {
                    await apiPostJson('/api/admin/student/status', { student_id: id, is_active: newStatus });
                    loadStudents();
                } catch (error) {
                    console.error('Error:', error);
                    notify('error', getApiErrorMessage(error, `Failed to ${action.toLowerCase()} student`), 'Error');
                }
            }
        });
    }
});

async function loadStudents() {
    try {
        const studentList = await apiGet('/api/admin/student/list');
        window.__studentListAll = Array.isArray(studentList) ? studentList : [];
        applyStudentFilter();
    } catch (error) {
        console.error('Failed to load students:', error);
    }
}

function applyStudentFilter() {
    const input = document.getElementById('studentSearchInput');
    const query = (input ? input.value : '').trim().toLowerCase();

    const list = Array.isArray(window.__studentListAll) ? window.__studentListAll : [];
    if (!query) {
        renderStudentTable(list);
        return;
    }

    const filtered = list.filter(student => {
        const statusText = student.is_active ? 'active' : 'inactive';
        const haystack = [
            student.enrollment_no,
            student.name,
            student.email,
            student.department,
            String(student.semester ?? ''),
            statusText,
            String(student.student_id ?? '')
        ]
            .filter(Boolean)
            .join(' ')
            .toLowerCase();
        return haystack.includes(query);
    });

    renderStudentTable(filtered);
}

function renderStudentTable(studentList) {
    const tbody = document.getElementById('studentTableBody');
    if (!tbody) return;

    tbody.innerHTML = '';
    if (!Array.isArray(studentList) || studentList.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center py-4 text-muted">No matching students found.</td></tr>';
        return;
    }

    studentList.forEach(student => {
        const row = document.createElement('tr');
        const initials = (student.name || '')
            .split(' ')
            .filter(Boolean)
            .map(n => n[0])
            .join('')
            .substring(0, 2)
            .toUpperCase();

        row.innerHTML = `
            <td class="ps-4 font-monospace text-muted">${student.enrollment_no || ''}</td>
            <td>
                <div class="d-flex align-items-center">
                    <div class="avatar-circle bg-primary text-white me-2" style="width: 35px; height: 35px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.85rem; font-weight: bold;">${initials || '?'}</div>
                    <div class="fw-semibold">${student.name || ''}</div>
                </div>
            </td>
            <td>${student.department || ''}</td>
            <td>${student.semester ?? ''}</td>
            <td>
                <span class="badge ${student.is_active ? 'bg-success-subtle text-success' : 'bg-danger-subtle text-danger'}">
                    ${student.is_active ? 'Active' : 'Inactive'}
                </span>
            </td>
            <td class="text-end pe-4">
                <button type="button" class="btn btn-sm btn-light text-primary js-edit-student" data-id="${student.student_id}" title="Edit"><i class="fas fa-edit"></i></button>
                <button type="button" class="btn btn-sm btn-light ${student.is_active ? 'text-danger' : 'text-success'} js-toggle-student-status" data-id="${student.student_id}" title="${student.is_active ? 'Deactivate' : 'Activate'}">
                    <i class="fas ${student.is_active ? 'fa-user-slash' : 'fa-user-check'}"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function openStudentEditModal(student) {
    const modalEl = document.getElementById('addStudentModal');
    const form = document.getElementById('addStudentForm');
    if (!modalEl || !form) return;

    const titleEl = modalEl.querySelector('.modal-title');
    if (titleEl) titleEl.innerHTML = '<i class="fas fa-user-plus me-2"></i>Edit Student';

    document.getElementById('studentId').value = student.student_id;
    document.getElementById('studentName').value = student.name || '';
    document.getElementById('studentEmail').value = student.email || '';
    document.getElementById('department').value = student.department || '';

    const semEl = document.getElementById('semester');
    if (semEl) {
        // best-effort match (options are labels like "1st Sem")
        const semesterInt = parseInt(student.semester);
        const options = Array.from(semEl.options);
        const match = options.find(o => parseInt(o.textContent) === semesterInt);
        if (match) semEl.value = match.value;
    }

    const enrollEl = document.getElementById('enrollmentNo');
    if (enrollEl) {
        enrollEl.value = student.enrollment_no || '';
        enrollEl.setAttribute('disabled', 'disabled');
    }

    const pw = document.getElementById('studentPassword');
    if (pw) {
        pw.value = '';
        pw.placeholder = 'Leave blank to keep unchanged';
        pw.removeAttribute('required');
    }

    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) submitBtn.innerHTML = '<i class="fas fa-save me-2"></i>Save Changes';

    form.classList.remove('was-validated');
    const modal = new bootstrap.Modal(modalEl);
    modal.show();
}

function resetStudentFormMode() {
    const modalEl = document.getElementById('addStudentModal');
    const form = document.getElementById('addStudentForm');
    if (!modalEl || !form) return;

    const titleEl = modalEl.querySelector('.modal-title');
    if (titleEl) titleEl.innerHTML = '<i class="fas fa-user-plus me-2"></i>Add New Student';

    const enrollEl = document.getElementById('enrollmentNo');
    if (enrollEl) enrollEl.removeAttribute('disabled');

    const pw = document.getElementById('studentPassword');
    if (pw) {
        pw.value = '';
        pw.placeholder = 'Initial Password (min 6 chars)';
        pw.setAttribute('required', 'required');
    }

    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) submitBtn.innerHTML = '<i class="fas fa-save me-2"></i>Save Student';
}
