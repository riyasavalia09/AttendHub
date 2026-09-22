document.addEventListener('DOMContentLoaded', function() {
    // Select all links/buttons that look like logout actions
    // 1. Explicit class 'logout-action'
    // 2. Explicit ID 'logoutBtn'
    // 3. Links pointing to login pages that contain "Logout" text
    const logoutLinks = document.querySelectorAll('.logout-action, #logoutBtn, a[href*="login.html"], a[href*="/login"]');

    logoutLinks.forEach(link => {
        // Double check text content for generic links to avoid catching actual login links if any
        // For buttons or ID matches, we assume they are correct
        const isGenericLink = link.tagName === 'A' && !link.classList.contains('logout-action') && link.id !== 'logoutBtn';
        
        if (!isGenericLink || link.textContent.trim().toLowerCase().includes('logout')) {
            
            link.addEventListener('click', async function(e) {
                e.preventDefault();

                if (typeof window.glassConfirm === 'function') {
                    const ok = await window.glassConfirm({
                        type: 'warning',
                        title: 'Logout',
                        message: 'Are you sure you want to logout?',
                        confirmText: 'Logout',
                        cancelText: 'Cancel'
                    });
                    if (!ok) return;
                }

                try {
                    if (window.apiPostJson) {
                        await window.apiPostJson('/api/auth/logout', {});
                    } else {
                        await fetch('/api/auth/logout', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({}) // Session ID handled by cookie
                        });
                    }

                    // Regardless of server response, we redirect to login
                    // Determine redirect URL based on current user context
                    let redirectUrl = '/';
                    const path = window.location.pathname;
                    
                    if (path.includes('/admin')) redirectUrl = '/admin/login';
                    else if (path.includes('/faculty')) redirectUrl = '/faculty/login';
                    else if (path.includes('/student')) redirectUrl = '/student/login';
                    
                    window.location.href = redirectUrl;

                } catch (error) {
                    console.error('Logout error:', error);
                    window.location.href = '/';
                }
            });
        }
    });
});
