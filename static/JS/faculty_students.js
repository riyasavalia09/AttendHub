(function () {
    let allStudents = [];
    let eventsWired = false;

    function notify(type, message, title) {
        if (typeof window.showToast === 'function') {
            window.showToast({ type, title: title || undefined, message });
            return;
        }
        console.warn(`[${type}] ${title ? `${title}: ` : ''}${message}`);
    }

    function initials(name) {
        const parts = String(name || '').trim().split(/\s+/).filter(Boolean);
        const first = parts[0]?.[0] || '';
        const last = parts.length > 1 ? parts[parts.length - 1][0] : '';
        const out = (first + last).toUpperCase();
        return out || '?';
    }

    function statusBadge(isActive) {
        if (isActive === false || isActive === 0) return { label: 'Inactive', cls: 'bg-danger' };
        return { label: 'Active', cls: 'bg-success' };
    }

    function escapeHtml(str) {
        return String(str ?? '')
            .replaceAll('&', '&amp;')
            .replaceAll('<', '&lt;')
            .replaceAll('>', '&gt;')
            .replaceAll('"', '&quot;')
            .replaceAll("'", '&#039;');
    }

    function setModal(student) {
        const modalInitials = document.getElementById('studentModalInitials');
        const modalName = document.getElementById('studentModalName');
        const modalIdLine = document.getElementById('studentModalIdLine');
        const modalStatus = document.getElementById('studentModalStatus');
        const modalEnrollment = document.getElementById('studentModalEnrollment');
        const modalDepartment = document.getElementById('studentModalDepartment');
        const modalSemester = document.getElementById('studentModalSemester');
        const modalEmail = document.getElementById('studentModalEmail');

        if (modalInitials) modalInitials.textContent = initials(student?.name);
        if (modalName) modalName.textContent = student?.name || '-';
        if (modalIdLine) modalIdLine.textContent = `Student ID: ${student?.student_id ?? '-'}`;

        const badge = statusBadge(student?.is_active);
        if (modalStatus) {
            modalStatus.className = `badge ${badge.cls}`;
            modalStatus.textContent = badge.label;
        }

        if (modalEnrollment) modalEnrollment.textContent = student?.enrollment_no || '-';
        if (modalDepartment) modalDepartment.textContent = student?.department || '-';
        if (modalSemester) modalSemester.textContent = student?.semester != null ? `Semester ${student.semester}` : '-';
        if (modalEmail) modalEmail.textContent = student?.email || '-';
    }

    function getFilters() {
        const dept = document.getElementById('departmentFilter')?.value || '';
        const sem = document.getElementById('semesterFilter')?.value || '';
        const q = (document.getElementById('studentSearchInput')?.value || '').trim().toLowerCase();
        return { dept, sem, q };
    }

    function applyFilters() {
        const { dept, sem, q } = getFilters();

        return allStudents.filter((s) => {
            if (!s || typeof s !== 'object') return false;

            if (dept && String(s.department) !== dept) return false;
            if (sem && String(s.semester) !== sem) return false;

            if (!q) return true;

            const haystack = `${s.name || ''} ${s.enrollment_no || ''} ${s.email || ''} ${s.student_id || ''}`.toLowerCase();
            return haystack.includes(q);
        });
    }

    function renderTable(rows) {
        const tbody = document.getElementById('studentTableBody');
        if (!tbody) return;

        const items = Array.isArray(rows) ? rows : [];

        if (!items.length) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7">
                        <div class="text-muted small py-3">No students found.</div>
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = items
            .map((s) => {
                const badge = statusBadge(s?.is_active);
                return `
                    <tr>
                        <td class="fw-bold text-secondary">${escapeHtml(s?.student_id)}</td>
                        <td>
                            <div class="d-flex align-items-center">
                                <div class="rounded-circle bg-light d-flex align-items-center justify-content-center me-3 border" style="width: 35px; height: 35px;">
                                    <span class="small fw-bold text-dark">${escapeHtml(initials(s?.name))}</span>
                                </div>
                                <span class="fw-medium">${escapeHtml(s?.name || '-')}</span>
                            </div>
                        </td>
                        <td>${escapeHtml(s?.enrollment_no || '-')}</td>
                        <td>${escapeHtml(s?.department || '-')}</td>
                        <td>${s?.semester != null ? `Sem ${escapeHtml(s.semester)}` : '-'}</td>
                        <td><span class="badge ${badge.cls}">${badge.label}</span></td>
                        <td class="text-end">
                            <button class="btn btn-sm btn-outline-primary" data-student-id="${escapeHtml(s?.student_id)}" data-bs-toggle="modal" data-bs-target="#studentModal">
                                <i class="fas fa-eye me-1"></i> View Profile
                            </button>
                        </td>
                    </tr>
                `;
            })
            .join('');
    }

    function populateFilters(students) {
        const deptSelect = document.getElementById('departmentFilter');
        const semSelect = document.getElementById('semesterFilter');
        if (!deptSelect || !semSelect) return;

        const departments = Array.from(
            new Set((students || []).map((s) => s?.department).filter(Boolean).map((d) => String(d)))
        ).sort();

        const semesters = Array.from(
            new Set((students || []).map((s) => s?.semester).filter((v) => v !== null && v !== undefined).map((v) => String(v)))
        ).sort((a, b) => Number(a) - Number(b));

        deptSelect.innerHTML = '<option value="">All</option>' + departments.map((d) => `<option value="${escapeHtml(d)}">${escapeHtml(d)}</option>`).join('');
        semSelect.innerHTML = '<option value="">All</option>' + semesters.map((s) => `<option value="${escapeHtml(s)}">Semester ${escapeHtml(s)}</option>`).join('');
    }

    function wireEvents() {
        if (eventsWired) return;
        eventsWired = true;

        const deptSelect = document.getElementById('departmentFilter');
        const semSelect = document.getElementById('semesterFilter');
        const search = document.getElementById('studentSearchInput');
        const addStudentForm = document.getElementById('addStudentForm');
        const addStudentModalEl = document.getElementById('addStudentModal');

        const rerender = () => renderTable(applyFilters());

        deptSelect?.addEventListener('change', rerender);
        semSelect?.addEventListener('change', rerender);
        search?.addEventListener('input', rerender);

        document.addEventListener('click', (e) => {
            const btn = e.target?.closest?.('button[data-student-id]');
            if (!btn) return;

            const studentId = btn.getAttribute('data-student-id');
            const student = allStudents.find((s) => String(s?.student_id) === String(studentId));
            setModal(student);
        });

        addStudentForm?.addEventListener('submit', async (e) => {
            e.preventDefault();

            if (!addStudentForm.checkValidity()) {
                addStudentForm.classList.add('was-validated');
                return;
            }

            const name = document.getElementById('studentName')?.value?.trim();
            const enrollmentNo = document.getElementById('enrollmentNo')?.value?.trim();
            const email = document.getElementById('studentEmail')?.value?.trim();
            const department = document.getElementById('department')?.value;
            const semesterRaw = document.getElementById('semester')?.value;
            const password = document.getElementById('studentPassword')?.value || '';
            const semester = parseInt(semesterRaw, 10);

            if (!Number.isInteger(semester) || semester < 1) {
                notify('warning', 'Please select a valid semester', 'Validation');
                return;
            }

            if (password.length < 6) {
                notify('warning', 'Password must be at least 6 characters', 'Validation');
                return;
            }

            const payload = {
                name,
                enrollment_no: enrollmentNo,
                email,
                department,
                semester,
                password
            };

            const submitBtn = addStudentForm.querySelector('button[type="submit"]');
            const originalBtnHtml = submitBtn ? submitBtn.innerHTML : '';
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Saving...';
            }

            try {
                await window.apiPostJson('/api/faculty/student/create', payload);

                addStudentForm.reset();
                addStudentForm.classList.remove('was-validated');
                const addModal = addStudentModalEl ? bootstrap.Modal.getOrCreateInstance(addStudentModalEl) : null;
                addModal?.hide();

                notify('success', 'Student added successfully', 'Success');
                await loadStudents();
            } catch (err) {
                notify('error', window.getApiErrorMessage(err, 'Failed to add student'), 'Error');
            } finally {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalBtnHtml;
                }
            }
        });
    }

    async function loadStudents() {
        try {
            const data = await window.apiGet('/api/faculty/students/list');
            allStudents = Array.isArray(data) ? data : [];
            populateFilters(allStudents);
            wireEvents();
            renderTable(applyFilters());
        } catch (err) {
            console.error(window.getApiErrorMessage(err, 'Failed to load students'));
            allStudents = [];
            renderTable([]);
        }
    }

    document.addEventListener('DOMContentLoaded', loadStudents);
})();
