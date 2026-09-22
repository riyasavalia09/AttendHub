/**
 * Glassmorphism Toast Notification System
 * Handles displaying beautiful glass-styled toast notifications.
 */

(function() {
    // Create container if it doesn't exist
    function getToastContainer() {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            document.body.appendChild(container);
        }
        return container;
    }

    /**
     * Show a toast notification
     * @param {Object} options 
     * @param {string} options.type - 'success', 'error', 'warning', 'info'
     * @param {string} options.title - Title of the toast
     * @param {string} options.message - Body text
     * @param {number} options.duration - Duration in ms (default 3000)
     */
    window.showToast = function({ type = 'info', title, message, duration = 3000 }) {
        const container = getToastContainer();
        
        // Define icons and colors based on type
        const config = {
            success: { icon: 'fa-check-circle', glowColor: 'rgba(40, 167, 69, 0.5)' },
            error: { icon: 'fa-exclamation-circle', glowColor: 'rgba(220, 53, 69, 0.5)' },
            warning: { icon: 'fa-exclamation-triangle', glowColor: 'rgba(255, 193, 7, 0.5)' },
            info: { icon: 'fa-info-circle', glowColor: 'rgba(23, 162, 184, 0.5)' }
        };
        
        const typeConfig = config[type] || config.info;
        
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `toast-glass toast-${type}`;
        toast.style.setProperty('--toast-glow', typeConfig.glowColor);
        
        toast.innerHTML = `
            <div class="toast-icon">
                <i class="fas ${typeConfig.icon}"></i>
            </div>
            <div class="toast-content">
                <div class="toast-title">${title || type.charAt(0).toUpperCase() + type.slice(1)}</div>
                <div class="toast-message">${message || ''}</div>
            </div>
            <button class="toast-close">&times;</button>
        `;

        // Append to container
        container.appendChild(toast);

        // Slide in animation logic is handled by CSS keyframes on .toast-glass

        // Close button handler
        const closeBtn = toast.querySelector('.toast-close');
        closeBtn.addEventListener('click', () => {
            removeToast(toast);
        });

        // Auto remove
        if (duration > 0) {
            setTimeout(() => {
                removeToast(toast);
            }, duration);
        }
    };

    function removeToast(toast) {
        toast.style.animation = 'toastSlideOut 0.3s forwards';
        toast.addEventListener('animationend', () => {
            if (toast.parentElement) {
                toast.parentElement.removeChild(toast);
            }
        });
    }

    // Expose simpler helpers
    window.showSuccess = (msg) => window.showToast({ type: 'success', title: 'Success', message: msg });
    window.showError = (msg) => window.showToast({ type: 'error', title: 'Error', message: msg });

})();
