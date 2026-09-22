(function () {
    function safeText(value, fallback) {
        const v = (value ?? '').toString().trim();
        return v ? v : (fallback ?? '—');
    }

    function initialsFromName(name) {
        const parts = (name ?? '').toString().trim().split(/\s+/).filter(Boolean);
        if (!parts.length) return '--';
        const first = parts[0][0] || '';
        const last = (parts.length > 1 ? parts[parts.length - 1][0] : parts[0][1]) || '';
        return (first + last).toUpperCase();
    }

    function formatDate(iso) {
        if (!iso) return '—';
        const d = new Date(iso);
        if (Number.isNaN(d.getTime())) return safeText(iso, '—');
        return d.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: '2-digit' });
    }

    function setBadge(el, { text, variant }) {
        if (!el) return;
        const icon = el.querySelector('i');
        const iconHtml = icon ? icon.outerHTML : '';

        el.classList.remove('bg-success', 'bg-danger', 'bg-info', 'bg-secondary', 'text-dark');
        if (variant) {
            const classes = variant
                .toString()
                .split(/\s+/)
                .map((c) => c.trim())
                .filter(Boolean);
            classes.forEach((c) => el.classList.add(c));
        }

        // Keep existing icon if present
        el.innerHTML = iconHtml ? `${iconHtml} ${text}` : text;
    }

    async function loadProfile() {
        const data = await window.apiGet('/api/admin/university/profile');
        const university = data?.university;
        const admin = data?.admin;

        // Navbar
        const navbarAdminName = document.getElementById('navbarAdminName');
        if (navbarAdminName) navbarAdminName.textContent = safeText(admin?.name, 'Admin');

        // University fields
        const uniNameInput = document.getElementById('uniNameInput');
        const uniIdInput = document.getElementById('uniIdInput');
        const registeredAddressInput = document.getElementById('registeredAddressInput');
        const contactEmailInput = document.getElementById('contactEmailInput');
        const contactPhoneInput = document.getElementById('contactPhoneInput');
        const websiteUrlInput = document.getElementById('websiteUrlInput');

        if (uniNameInput) uniNameInput.value = university?.university_name ?? '';
        if (uniIdInput) uniIdInput.value = university?.university_id_display ?? '';
        if (registeredAddressInput) registeredAddressInput.value = university?.registered_address ?? '';
        if (contactEmailInput) contactEmailInput.value = university?.official_contact_email ?? '';
        if (contactPhoneInput) contactPhoneInput.value = university?.official_contact_phone ?? '';
        if (websiteUrlInput) websiteUrlInput.value = university?.website_url ?? '';

        // Badges
        const systemStatusBadge = document.getElementById('systemStatusBadge');
        const planBadge = document.getElementById('planBadge');

        const isActive = Boolean(university?.is_active);
        setBadge(systemStatusBadge, {
            text: isActive ? 'System Active' : 'System Inactive',
            variant: isActive ? 'bg-success' : 'bg-danger'
        });

        const plan = (university?.plan ?? 'FREE').toString().toUpperCase();
        setBadge(planBadge, {
            text: plan === 'PREMIUM' ? 'Premium License' : 'Free License',
            variant: plan === 'PREMIUM' ? 'bg-info text-dark' : 'bg-info text-dark'
        });

        // Admin card
        const adminInitials = document.getElementById('adminInitials');
        const adminNameText = document.getElementById('adminNameText');
        const adminRoleText = document.getElementById('adminRoleText');
        const adminRoleValue = document.getElementById('adminRoleValue');
        const adminStatusBadge = document.getElementById('adminStatusBadge');
        const adminEmailText = document.getElementById('adminEmailText');
        const adminCreatedText = document.getElementById('adminCreatedText');

        const adminName = admin?.name;
        if (adminInitials) adminInitials.textContent = initialsFromName(adminName);
        if (adminNameText) adminNameText.textContent = safeText(adminName, 'Admin');
        if (adminRoleText) adminRoleText.textContent = 'System Administrator';
        if (adminRoleValue) adminRoleValue.textContent = 'Admin';

        const verified = Boolean(admin?.is_verified);
        if (adminStatusBadge) {
            adminStatusBadge.classList.remove('bg-success', 'bg-warning');
            adminStatusBadge.classList.add(verified ? 'bg-success' : 'bg-warning');
            adminStatusBadge.textContent = verified ? 'Verified' : 'Unverified';
        }

        if (adminEmailText) adminEmailText.textContent = safeText(admin?.email, '—');
        if (adminCreatedText) adminCreatedText.textContent = formatDate(admin?.created_at);
    }

    async function saveProfile() {
        const btn = document.getElementById('saveUniversityProfileBtn');
        const uniNameInput = document.getElementById('uniNameInput');
        const registeredAddressInput = document.getElementById('registeredAddressInput');
        const contactEmailInput = document.getElementById('contactEmailInput');
        const contactPhoneInput = document.getElementById('contactPhoneInput');
        const websiteUrlInput = document.getElementById('websiteUrlInput');

        const payload = {
            university_name: uniNameInput?.value ?? '',
            registered_address: registeredAddressInput?.value ?? '',
            official_contact_email: contactEmailInput?.value ?? '',
            official_contact_phone: contactPhoneInput?.value ?? '',
            website_url: websiteUrlInput?.value ?? ''
        };

        if (btn) {
            btn.disabled = true;
            btn.dataset.originalText = btn.innerHTML;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Saving...';
        }

        try {
            await window.apiPostJson('/api/admin/university/profile/update', payload);
            await loadProfile();
            if (typeof window.showToast === 'function') {
                window.showToast({ type: 'success', title: 'Saved', message: 'University profile saved' });
            }
        } catch (err) {
            if (typeof window.showToast === 'function') {
                window.showToast({ type: 'error', title: 'Error', message: window.getApiErrorMessage(err, 'Failed to save profile') });
            }
        } finally {
            if (btn) {
                btn.disabled = false;
                btn.innerHTML = btn.dataset.originalText || '<i class="fas fa-save me-2"></i>Save Changes';
            }
        }
    }

    document.addEventListener('DOMContentLoaded', function () {
        loadProfile().catch((err) => {
            console.error(err);
            if (typeof window.showToast === 'function') {
                window.showToast({ type: 'error', title: 'Error', message: window.getApiErrorMessage(err, 'Failed to load university profile') });
            }
        });

        const saveBtn = document.getElementById('saveUniversityProfileBtn');
        if (saveBtn) saveBtn.addEventListener('click', saveProfile);
    });
})();
