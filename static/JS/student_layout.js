document.addEventListener('DOMContentLoaded', () => {
    // Student pages reuse these navbar placeholders; fill them consistently.
    hydrateStudentNavbar().catch(() => {
        // Silent fail: pages should remain usable even if profile endpoint errors.
    });
});

async function hydrateStudentNavbar() {
    const nameTopEl = document.getElementById('studentNameTop');
    const avatarTopEl = document.getElementById('studentAvatarTop');

    // If this page doesn't have the navbar placeholders, nothing to do.
    if (!nameTopEl && !avatarTopEl) return;

    // apiGet is provided by static/JS/api.js
    if (typeof apiGet !== 'function') return;

    const p = await apiGet('/api/student/profile');
    const name = p?.name || 'Student';

    if (nameTopEl) nameTopEl.textContent = name;

    if (avatarTopEl) {
        const avatarUrlSmall = `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=random&size=64`;
        avatarTopEl.src = avatarUrlSmall;
    }
}
