(function () {
    function qs(name) {
        return new URLSearchParams(window.location.search).get(name);
    }

    function setLoading(btn, loading, text) {
        if (!btn) return;
        if (loading) {
            btn.disabled = true;
            btn.dataset.originalText = btn.innerHTML;
            btn.innerHTML = `<i class="fas fa-spinner fa-spin me-2"></i>${text || 'Working...'}`;
        } else {
            btn.disabled = false;
            btn.innerHTML = btn.dataset.originalText || btn.innerHTML;
        }
    }

    function showError(input, msg) {
        if (!input) return;
        input.classList.add('is-invalid');
        const err = input.nextElementSibling;
        if (err && err.classList.contains('error-message')) {
            err.textContent = msg;
            err.style.color = '#dc3545';
            err.style.fontSize = '0.875rem';
            err.style.marginTop = '0.25rem';
        }
    }

    function clearErrors(form) {
        if (!form) return;
        form.querySelectorAll('.is-invalid').forEach((el) => el.classList.remove('is-invalid'));
        form.querySelectorAll('.error-message').forEach((el) => (el.textContent = ''));
    }

    function setIdentifierLabel(role) {
        const label = document.getElementById('fpIdentifierLabel');
        const input = document.getElementById('fpIdentifier');
        const back = document.getElementById('backToLoginLink');
        if (!label || !input) return;

        if (role === 'student') {
            label.textContent = 'Enrollment No';
            input.placeholder = 'Enter your enrollment number';
            if (back) back.href = '/student/login';
        } else {
            label.textContent = 'Email';
            input.placeholder = 'Enter your email';
            if (back) back.href = role === 'faculty' ? '/faculty/login' : '/admin/login';
        }
    }

    async function onForgotSubmit(e) {
        e.preventDefault();

        const form = document.getElementById('forgotPasswordForm');
        const roleEl = document.getElementById('fpRole');
        const identifierEl = document.getElementById('fpIdentifier');
        const tokenBox = document.getElementById('fpTokenBox');
        const tokenValue = document.getElementById('fpTokenValue');
        const expiresText = document.getElementById('fpExpiresText');
        const submitBtn = form?.querySelector('button[type="submit"]');

        clearErrors(form);

        const role = (roleEl?.value || '').trim();
        const identifier = (identifierEl?.value || '').trim();

        if (!role) {
            showError(roleEl, 'Role is required');
            return;
        }
        if (!identifier) {
            showError(identifierEl, 'This field is required');
            return;
        }

        setLoading(submitBtn, true, 'Generating...');
        try {
            const res = await window.apiPostJson('/api/auth/forgot-password', {
                role,
                identifier,
            });

            const data = res?.data || res;
            const token = data?.token;
            const expiresIn = data?.expires_in_seconds;

            if (typeof window.showToast === 'function') {
                window.showToast({
                    type: 'success',
                    title: 'Done',
                    message: String(res?.message || data?.message || 'Done')
                });
            }

            if (token) {
                if (tokenValue) tokenValue.value = token;
                if (expiresText) {
                    expiresText.textContent = expiresIn ? `Expires in ~${Math.round(expiresIn / 60)} minutes` : '';
                }
                if (tokenBox) tokenBox.classList.remove('d-none');

                const rpToken = document.getElementById('rpToken');
                if (rpToken && !rpToken.value) rpToken.value = token;
            }
        } catch (err) {
            if (typeof window.showToast === 'function') {
                window.showToast({ type: 'error', title: 'Error', message: window.getApiErrorMessage(err, 'Failed to generate token') });
            }
        } finally {
            setLoading(submitBtn, false);
        }
    }

    async function onResetSubmit(e) {
        e.preventDefault();

        const form = document.getElementById('resetPasswordForm');
        const tokenEl = document.getElementById('rpToken');
        const newEl = document.getElementById('rpNewPassword');
        const confirmEl = document.getElementById('rpConfirmPassword');
        const submitBtn = form?.querySelector('button[type="submit"]');

        clearErrors(form);

        const token = (tokenEl?.value || '').trim();
        const newPassword = newEl?.value || '';
        const confirmPassword = confirmEl?.value || '';

        if (!token) {
            showError(tokenEl, 'Token is required');
            return;
        }
        if (!newPassword || newPassword.length < 6) {
            showError(newEl, 'Password must be at least 6 characters');
            return;
        }
        if (newPassword !== confirmPassword) {
            showError(confirmEl, 'Passwords do not match');
            return;
        }

        setLoading(submitBtn, true, 'Resetting...');
        try {
            await window.apiPostJson('/api/auth/reset-password', {
                token,
                new_password: newPassword,
            });
            if (typeof window.showToast === 'function') {
                window.showToast({ type: 'success', title: 'Password Reset', message: 'Password reset successful. Please login.' });
            }

            // Best effort redirect by role in token is unknown on frontend; send to home.
            window.location.href = '/';
        } catch (err) {
            if (typeof window.showToast === 'function') {
                window.showToast({ type: 'error', title: 'Error', message: window.getApiErrorMessage(err, 'Failed to reset password') });
            }
        } finally {
            setLoading(submitBtn, false);
        }
    }

    function bindCopy() {
        const btn = document.getElementById('fpCopyTokenBtn');
        const input = document.getElementById('fpTokenValue');
        if (!btn || !input) return;
        btn.addEventListener('click', async function () {
            try {
                await navigator.clipboard.writeText(input.value || '');
            } catch {
                input.select();
                document.execCommand('copy');
            }
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        const roleEl = document.getElementById('fpRole');
        const preRole = (qs('role') || '').toLowerCase();
        if (roleEl && (preRole === 'admin' || preRole === 'faculty' || preRole === 'student')) {
            roleEl.value = preRole;
        }
        setIdentifierLabel(roleEl?.value);
        roleEl?.addEventListener('change', function () {
            setIdentifierLabel(roleEl.value);
        });

        document.getElementById('forgotPasswordForm')?.addEventListener('submit', onForgotSubmit);
        document.getElementById('resetPasswordForm')?.addEventListener('submit', onResetSubmit);
        bindCopy();
    });
})();
