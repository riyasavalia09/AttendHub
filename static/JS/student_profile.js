document.addEventListener('DOMContentLoaded', function () {
    loadStudentProfile();
});

function escapeHtml(str) {
    return String(str ?? '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#039;');
}

function setValue(id, value) {
    const el = document.getElementById(id);
    if (!el) return;
    if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
        el.value = value ?? '';
    } else {
        el.textContent = value ?? '—';
    }
}

async function loadStudentProfile() {
    try {
        const p = await apiGet('/api/student/profile');
        const name = p?.name || 'Student';

        const avatarUrl = `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=6CB1DA&color=fff&size=128`;
        const avatarUrlSmall = `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=random&size=64`;

        const avatar = document.getElementById('studentAvatar');
        if (avatar) avatar.src = avatarUrl;

        const avatarTop = document.getElementById('studentAvatarTop');
        if (avatarTop) avatarTop.src = avatarUrlSmall;

        const nameTop = document.getElementById('studentNameTop');
        if (nameTop) nameTop.textContent = name;

        setValue('studentNameHeading', name);
        setValue('studentName', name);
        setValue('studentEnrollment', p?.enrollment_no || '');
        setValue('studentDepartment', p?.department || '');
        setValue('studentSemester', p?.semester != null ? `Semester ${p.semester}` : '');
        setValue('studentEmail', p?.email || '');

        const status = document.getElementById('studentStatus');
        if (status) {
            const active = !!p?.is_active;
            status.className = `badge px-3 py-2 rounded-pill ${active ? 'bg-success' : 'bg-secondary'}`;
            status.textContent = active ? 'Active' : 'Inactive';
        }
    } catch (error) {
        console.error('Error loading profile:', error);
        // Don't hard-fail UI; show minimal hint
        const heading = document.getElementById('studentNameHeading');
        if (heading) heading.textContent = 'Profile unavailable';
    }
}
