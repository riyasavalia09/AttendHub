(function () {
    function byId(id) {
        return document.getElementById(id);
    }

    function safeText(value, fallback) {
        const v = (value ?? '').toString().trim();
        return v ? v : (fallback ?? '—');
    }

    function initialsFromName(name) {
        const n = (name ?? '').toString().trim();
        if (!n) return 'F';
        const parts = n.split(/\s+/).filter(Boolean);
        const first = parts[0]?.[0] || 'F';
        const second = (parts.length > 1 ? parts[1]?.[0] : parts[0]?.[1]) || '';
        return (first + second).toUpperCase();
    }

    async function loadFacultyContext() {
        if (!window.apiGet) return;

        const data = await window.apiGet('/api/faculty/context');
        const faculty = data?.faculty;

        const name = safeText(faculty?.name, 'Faculty');

        const navbarFacultyName = byId('navbarFacultyName');
        if (navbarFacultyName) navbarFacultyName.textContent = name;

        const navbarFacultyInitials = byId('navbarFacultyInitials');
        if (navbarFacultyInitials) navbarFacultyInitials.textContent = initialsFromName(name);

        // Notifications are currently not backed by real data.
        const notificationsNavItem = byId('notificationsNavItem');
        if (notificationsNavItem) notificationsNavItem.style.display = 'none';
    }

    document.addEventListener('DOMContentLoaded', function () {
        loadFacultyContext().catch((err) => {
            console.error('Failed to load faculty context:', err);
        });
    });
})();
