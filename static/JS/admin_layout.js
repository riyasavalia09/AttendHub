(function () {
    function byId(id) {
        return document.getElementById(id);
    }

    function safeText(value, fallback) {
        const v = (value ?? '').toString().trim();
        return v ? v : (fallback ?? '—');
    }

    function setBadge(el, { text, addClasses = [], removeClasses = [] }) {
        if (!el) return;
        removeClasses.forEach((c) => el.classList.remove(c));
        addClasses.forEach((c) => el.classList.add(c));
        el.textContent = text;
    }

    function initialsFromName(name) {
        const n = (name ?? '').toString().trim();
        if (!n) return 'A';
        const parts = n.split(/\s+/).filter(Boolean);
        const first = parts[0]?.[0] || 'A';
        const second = (parts.length > 1 ? parts[parts.length - 1]?.[0] : parts[0]?.[1]) || '';
        return (first + second).toUpperCase();
    }

    function setAdminAvatar(name) {
        const initials = initialsFromName(name);

        const navbarAdminName = byId('navbarAdminName');
        const navbarAvatar = navbarAdminName
            ?.closest('a')
            ?.querySelector('.rounded-circle');
        if (navbarAvatar) {
            navbarAvatar.innerHTML = `<span class="small fw-bold" style="color: rgba(7,10,16,0.92);">${initials}</span>`;
            navbarAvatar.setAttribute('aria-label', `Admin avatar ${initials}`);
        }

        const sidebarAdminName = byId('sidebarAdminName');
        const sidebarAvatar = sidebarAdminName
            ?.closest('.mini-profile')
            ?.querySelector('.who .avatar');
        if (sidebarAvatar) {
            sidebarAvatar.innerHTML = `<span class="small fw-bold" style="color: rgba(7,10,16,0.92);">${initials}</span>`;
            sidebarAvatar.setAttribute('aria-label', `Admin avatar ${initials}`);
        }
    }

    async function loadAdminContext() {
        if (!window.apiGet) return;

        const data = await window.apiGet('/api/admin/university/profile');
        const university = data?.university;
        const admin = data?.admin;

        const navbarAdminName = byId('navbarAdminName');
        const adminName = safeText(admin?.name, 'Admin');
        if (navbarAdminName) navbarAdminName.textContent = adminName;
        setAdminAvatar(adminName);

        const dashUniName = byId('dashboardUniversityName');
        if (dashUniName) dashUniName.textContent = safeText(university?.university_name, '—');

        const dashUniId = byId('dashboardUniversityId');
        if (dashUniId) dashUniId.textContent = safeText(university?.university_id_display, '—');

        const dashStatus = byId('dashboardSystemStatusBadge');
        if (dashStatus) {
            const active = Boolean(university?.is_active);
            setBadge(dashStatus, {
                text: active ? 'System Active' : 'System Inactive',
                addClasses: [active ? 'bg-success' : 'bg-danger'],
                removeClasses: ['bg-success', 'bg-danger']
            });
        }

        const dashPlan = byId('dashboardPlanBadge');
        if (dashPlan) {
            const plan = (university?.plan ?? 'FREE').toString().toUpperCase();
            setBadge(dashPlan, {
                text: plan === 'PREMIUM' ? 'Premium License' : 'Free License',
                addClasses: ['bg-info', 'text-dark'],
                removeClasses: []
            });
        }

        // Notifications are currently not backed by real data.
        // Hide the bell to avoid fake counts/text.
        const notificationsNavItem = byId('notificationsNavItem');
        if (notificationsNavItem) notificationsNavItem.style.display = 'none';
    }

    document.addEventListener('DOMContentLoaded', function () {
        setAdminAvatar('Admin');
        loadAdminContext().catch((err) => {
            console.error('Failed to load admin context:', err);
            // If session expired, pages will handle via API errors.
        });
    });
})();
