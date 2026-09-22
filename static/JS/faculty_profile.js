(function () {
    function setValue(id, value) {
        const el = document.getElementById(id);
        if (!el) return;
        if ('value' in el) {
            el.value = value ?? '';
        } else {
            el.textContent = value ?? '—';
        }
    }

    function setStatus(isActive) {
        const el = document.getElementById('profileStatus');
        if (!el) return;

        if (isActive === false || isActive === 0) {
            el.className = 'badge bg-danger';
            el.textContent = 'Inactive Faculty';
        } else {
            el.className = 'badge bg-success';
            el.textContent = 'Active Faculty';
        }
    }

    async function loadProfile() {
        try {
            const data = await window.apiGet('/api/faculty/profile');
            const faculty = data?.faculty || {};

            setValue('profileName', faculty?.name || '—');
            setStatus(faculty?.is_active);

            setValue('profileFacultyId', faculty?.faculty_id ?? '');
            setValue('profileDepartment', faculty?.department ?? '');
            setValue('profileEmail', faculty?.email ?? '');
        } catch (err) {
            console.error(window.getApiErrorMessage(err, 'Failed to load profile'));
            setValue('profileName', '—');
            setStatus(null);
        }
    }

    document.addEventListener('DOMContentLoaded', loadProfile);
})();
