// Lightweight API client for consistent fetch() handling across the app.
// Provides: apiGet, apiPostJson, apiPostForm, apiRequest

(function () {
    async function safeParseJson(response) {
        const contentType = response.headers.get('content-type') || '';
        if (!contentType.includes('application/json')) return null;
        try {
            return await response.json();
        } catch (_) {
            return null;
        }
    }

    function unwrapPayload(payload) {
        if (payload && typeof payload === 'object' && payload.status && Object.prototype.hasOwnProperty.call(payload, 'data')) {
            return payload.data;
        }
        return payload;
    }

    function extractMessage(payload, fallback) {
        if (!payload) return fallback;
        if (typeof payload === 'string') return payload;
        return payload.message || payload.error || fallback;
    }

    async function apiRequest(url, options) {
        const opts = options || {};
        const response = await fetch(url, opts);

        const payload = (await safeParseJson(response)) ?? { message: await response.text().catch(() => '') };
        const data = unwrapPayload(payload);

        if (!response.ok) {
            const message = extractMessage(payload, `Request failed (${response.status})`);
            const err = new Error(message);
            err.status = response.status;
            err.payload = payload;
            throw err;
        }

        return { data, payload, response };
    }

    async function apiGet(url) {
        const { data } = await apiRequest(url, { method: 'GET' });
        return data;
    }

    async function apiPostJson(url, json) {
        const { data } = await apiRequest(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(json ?? {})
        });
        return data;
    }

    async function apiPostForm(url, formData) {
        const { data } = await apiRequest(url, {
            method: 'POST',
            body: formData
        });
        return data;
    }

    function getApiErrorMessage(error, fallback) {
        if (!error) return fallback || 'Something went wrong';
        return error.message || fallback || 'Something went wrong';
    }

    function ensureToastRoot() {
        const existing = document.getElementById('toast-root');
        if (existing) return existing;

        if (!document.body) {
            return null;
        }

        const root = document.createElement('div');
        root.id = 'toast-root';
        root.className = 'toast-root';
        document.body.appendChild(root);
        return root;
    }

    function ensureDialogRoot() {
        const existing = document.getElementById('glass-dialog-root');
        if (existing) return existing;

        if (!document.body) {
            return null;
        }

        const root = document.createElement('div');
        root.id = 'glass-dialog-root';
        root.className = 'glass-dialog-root';
        document.body.appendChild(root);
        return root;
    }

    function dismissToast(toastEl) {
        if (!toastEl) return;
        toastEl.classList.add('toast--out');
        const remove = () => toastEl.remove();
        toastEl.addEventListener('animationend', remove, { once: true });
        setTimeout(remove, 260);
    }

    function showToast(options) {
        const opts = options || {};
        const type = (opts.type || 'success').toLowerCase();
        const message = String(opts.message || '');
        const title = String(opts.title || (type === 'error' ? 'Error' : type === 'warning' ? 'Warning' : 'Success'));
        const durationMs = Number.isFinite(opts.durationMs) ? opts.durationMs : 4000;

        let root = ensureToastRoot();
        if (!root) {
            document.addEventListener(
                'DOMContentLoaded',
                () => {
                    root = ensureToastRoot();
                    if (root) showToast(opts);
                },
                { once: true }
            );
            return;
        }

        const toast = document.createElement('div');
        toast.className = `toast toast--${type}`;
        toast.setAttribute('role', 'status');
        toast.setAttribute('aria-live', 'polite');

        const inner = document.createElement('div');
        inner.className = 'toast__inner';

        const bar = document.createElement('div');
        bar.className = 'toast__bar';

        const content = document.createElement('div');
        const t = document.createElement('p');
        t.className = 'toast__title';
        t.textContent = title;

        const m = document.createElement('p');
        m.className = 'toast__message';
        m.textContent = message;

        content.appendChild(t);
        if (message) content.appendChild(m);

        const close = document.createElement('button');
        close.className = 'toast__close';
        close.type = 'button';
        close.setAttribute('aria-label', 'Close notification');
        close.innerHTML = '&times;';
        close.addEventListener('click', () => dismissToast(toast));

        inner.appendChild(bar);
        inner.appendChild(content);
        inner.appendChild(close);
        toast.appendChild(inner);

        root.appendChild(toast);

        const timer = setTimeout(() => dismissToast(toast), Math.max(0, durationMs));
        toast.addEventListener('mouseenter', () => clearTimeout(timer), { once: true });
    }

    function glassConfirm(options) {
        const opts = options || {};
        const type = String(opts.type || 'warning').toLowerCase();
        const title = String(opts.title || 'Confirm');
        const message = String(opts.message || 'Are you sure?');
        const confirmText = String(opts.confirmText || 'Confirm');
        const cancelText = String(opts.cancelText || 'Cancel');

        return new Promise((resolve) => {
            let root = ensureDialogRoot();
            if (!root) {
                document.addEventListener(
                    'DOMContentLoaded',
                    () => {
                        glassConfirm(opts).then(resolve);
                    },
                    { once: true }
                );
                return;
            }

            const backdrop = document.createElement('div');
            backdrop.className = 'glass-dialog-backdrop';

            const dialog = document.createElement('div');
            dialog.className = `glass-dialog glass-dialog--${type}`;
            dialog.setAttribute('role', 'dialog');
            dialog.setAttribute('aria-modal', 'true');
            dialog.setAttribute('aria-label', title);
            dialog.tabIndex = -1;

            const header = document.createElement('div');
            header.className = 'glass-dialog__header';

            const h = document.createElement('h3');
            h.className = 'glass-dialog__title';
            h.textContent = title;

            const close = document.createElement('button');
            close.type = 'button';
            close.className = 'glass-dialog__close';
            close.setAttribute('aria-label', 'Close');
            close.innerHTML = '&times;';

            header.appendChild(h);
            header.appendChild(close);

            const body = document.createElement('div');
            body.className = 'glass-dialog__body';
            const p = document.createElement('p');
            p.className = 'glass-dialog__message';
            p.textContent = message;
            body.appendChild(p);

            const footer = document.createElement('div');
            footer.className = 'glass-dialog__footer';

            const cancelBtn = document.createElement('button');
            cancelBtn.type = 'button';
            cancelBtn.className = 'glass-dialog__btn glass-dialog__btn--cancel';
            cancelBtn.textContent = cancelText;

            const okBtn = document.createElement('button');
            okBtn.type = 'button';
            okBtn.className = 'glass-dialog__btn glass-dialog__btn--confirm';
            okBtn.textContent = confirmText;

            footer.appendChild(cancelBtn);
            footer.appendChild(okBtn);

            dialog.appendChild(header);
            dialog.appendChild(body);
            dialog.appendChild(footer);
            backdrop.appendChild(dialog);
            root.appendChild(backdrop);

            const cleanup = () => backdrop.remove();
            const finish = (value) => {
                cleanup();
                resolve(Boolean(value));
            };

            cancelBtn.addEventListener('click', () => finish(false));
            close.addEventListener('click', () => finish(false));
            okBtn.addEventListener('click', () => finish(true));

            backdrop.addEventListener('click', (e) => {
                if (e.target === backdrop) finish(false);
            });

            const onKey = (e) => {
                if (e.key === 'Escape') {
                    e.preventDefault();
                    document.removeEventListener('keydown', onKey);
                    finish(false);
                }
            };
            document.addEventListener('keydown', onKey);

            // Focus
            setTimeout(() => okBtn.focus(), 0);
        });
    }

    window.apiRequest = apiRequest;
    window.apiGet = apiGet;
    window.apiPostJson = apiPostJson;
    window.apiPostForm = apiPostForm;
    window.getApiErrorMessage = getApiErrorMessage;
    window.showToast = showToast;
    window.glassConfirm = glassConfirm;
    window.confirmGlass = glassConfirm;
})();
