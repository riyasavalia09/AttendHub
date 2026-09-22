(function () {
    function notify(type, message, title) {
        if (typeof window.showToast === 'function') {
            window.showToast({ type, title: title || undefined, message: String(message || '') });
        } else {
            console.warn(`[${type}] ${title ? title + ': ' : ''}${message}`);
        }
    }

    function getModal() {
        const el = document.getElementById('changePasswordModal');
        if (!el) return null;
        return bootstrap.Modal.getOrCreateInstance(el);
    }

    function clearFields() {
        const current = document.getElementById('cpCurrentPassword');
        const next = document.getElementById('cpNewPassword');
        const confirm = document.getElementById('cpConfirmPassword');
        if (current) current.value = '';
        if (next) next.value = '';
        if (confirm) confirm.value = '';
    }

    async function submitChangePassword() {
        const btn = document.getElementById('cpSubmitBtn');
        const current = document.getElementById('cpCurrentPassword');
        const next = document.getElementById('cpNewPassword');
        const confirm = document.getElementById('cpConfirmPassword');

        const currentPassword = current?.value || '';
        const newPassword = next?.value || '';
        const confirmPassword = confirm?.value || '';

        if (!currentPassword) return notify('warning', 'Current password is required', 'Validation');
        if (!newPassword || newPassword.length < 6) return notify('warning', 'New password must be at least 6 characters', 'Validation');
        if (newPassword !== confirmPassword) return notify('warning', 'New passwords do not match', 'Validation');

        if (btn) {
            btn.disabled = true;
            btn.dataset.originalText = btn.innerHTML;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Updating...';
        }

        try {
            await window.apiPostJson('/api/auth/change-password', {
                current_password: currentPassword,
                new_password: newPassword,
            });
            notify('success', 'Password updated successfully', 'Success');
            clearFields();
            getModal()?.hide();
        } catch (err) {
            notify('error', window.getApiErrorMessage(err, 'Failed to change password'), 'Error');
        } finally {
            if (btn) {
                btn.disabled = false;
                btn.innerHTML = btn.dataset.originalText || 'Update Password';
            }
        }
    }

    function wireButtons() {
        const openBtn = document.getElementById('changePasswordBtn');
        const openBtn2 = document.getElementById('changePasswordBtn2');
        const submitBtn = document.getElementById('cpSubmitBtn');

        function open() {
            clearFields();
            getModal()?.show();
        }

        if (openBtn) openBtn.addEventListener('click', open);
        if (openBtn2) openBtn2.addEventListener('click', open);
        if (submitBtn) submitBtn.addEventListener('click', submitChangePassword);
    }

    document.addEventListener('DOMContentLoaded', wireButtons);
})();
