// API Configuration
const API_BASE_URL = '/api/auth';

// Admin Signup Handler
if (document.getElementById('adminSignupForm')) {
    const form = document.getElementById('adminSignupForm');
    const universityName = document.getElementById('universityName');
    const adminName = document.getElementById('adminName');
    const email = document.getElementById('email');
    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('confirmPassword');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Clear previous errors
        clearValidationErrors();
        
        // Validation
        let isValid = true;

        if (universityName.value.trim() === '') {
            showError(universityName, 'University name is required');
            isValid = false;
        }

        if (adminName.value.trim() === '') {
            showError(adminName, 'Admin name is required');
            isValid = false;
        }

        if (email.value.trim() === '') {
            showError(email, 'Email is required');
            isValid = false;
        } else if (!validateEmail(email.value)) {
            showError(email, 'Please enter a valid email address');
            isValid = false;
        }

        if (password.value === '') {
            showError(password, 'Password is required');
            isValid = false;
        } else if (password.value.length < 6) {
            showError(password, 'Password must be at least 6 characters');
            isValid = false;
        }

        if (confirmPassword.value === '') {
            showError(confirmPassword, 'Please confirm your password');
            isValid = false;
        } else if (password.value !== confirmPassword.value) {
            showError(confirmPassword, 'Passwords do not match');
            isValid = false;
        }

        if (!isValid) return;

        // Auto-detect domain from email for the 'location' (mapped to domain in DB)
        const emailVal = email.value.trim();
        const domain = emailVal.substring(emailVal.lastIndexOf("@") + 1);

        // Prepare payload
        const payload = {
            university_name: universityName.value.trim(),
            location: domain, 
            admin_name: adminName.value.trim(),
            email: emailVal,
            password: password.value
        };

        // Show loading state
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Creating Account...';

        try {
            await apiPostJson(`${API_BASE_URL}/admin/signup`, payload);
            if (window.showToast) {
                window.showToast({ type: 'success', title: 'Account Created', message: 'Account created successfully! Please login.' });
            }
            window.location.href = '/admin/login';
        } catch (error) {
            console.error('Error:', error);
            const msg = (window.getApiErrorMessage && window.getApiErrorMessage(error, 'Signup failed. Please try again.')) || (error && error.message) || 'Signup failed. Please try again.';

            // Always show inline error so it's visible even if toast is missed.
            // Common case: duplicate email.
            showError(email, msg);
            email.focus();

            if (window.showToast) {
                window.showToast({ type: 'error', title: 'Signup Failed', message: msg });
            }
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
        }
    });
}

// Admin Login Handler
if (document.getElementById('loginForm') && window.location.pathname.includes('/admin/login')) {
    const form = document.getElementById('loginForm');
    const loginId = document.getElementById('loginId');
    const password = document.getElementById('password');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        clearValidationErrors();
        
        // Validation
        let isValid = true;

        if (loginId.value.trim() === '') {
            showError(loginId, 'Email is required');
            isValid = false;
        } else if (!validateEmail(loginId.value.trim())) {
            showError(loginId, 'Please enter a valid email address');
            isValid = false;
        }

        if (password.value === '') {
            showError(password, 'Password is required');
            isValid = false;
        } else if (password.value.length < 6) {
            showError(password, 'Password must be at least 6 characters');
            isValid = false;
        }

        if (!isValid) return;

        // Prepare payload
        const payload = {
            email: loginId.value.trim(),
            password: password.value
        };

        // Show loading state
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Logging in...';

        try {
            await apiPostJson(`${API_BASE_URL}/admin/login`, payload);
            if (window.showToast) {
                window.showToast({ type: 'success', title: 'Login Successful', message: 'Welcome back.' });
            }
            window.location.href = '/admin/dashboard';
        } catch (error) {
            console.error('Error:', error);
            const msg = (window.getApiErrorMessage && window.getApiErrorMessage(error, 'Login failed. Please check your credentials.')) || (error && error.message) || 'Login failed. Please check your credentials.';

            // Inline red error (requested UX)
            showError(loginId, msg);
            showError(password, msg);
            loginId.focus();

            if (window.showToast) {
                window.showToast({ type: 'error', title: 'Invalid Login', message: msg });
            }
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
        }
    });
}

// Faculty Login Handler
if (document.getElementById('loginForm') && window.location.pathname.includes('/faculty/login')) {
    const form = document.getElementById('loginForm');
    const loginId = document.getElementById('loginId');
    const password = document.getElementById('password');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        clearValidationErrors();
        
        let isValid = true;

        if (loginId.value.trim() === '') {
            showError(loginId, 'Faculty ID or Email is required');
            isValid = false;
        }

        if (password.value === '') {
            showError(password, 'Password is required');
            isValid = false;
        } else if (password.value.length < 6) {
            showError(password, 'Password must be at least 6 characters');
            isValid = false;
        }

        if (!isValid) return;

        const payload = {
            email: loginId.value.trim(),
            password: password.value
        };

        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Logging in...';

        try {
            await apiPostJson(`${API_BASE_URL}/faculty/login`, payload);
            if (window.showToast) {
                window.showToast({ type: 'success', title: 'Login Successful', message: 'Welcome back.' });
            }
            window.location.href = '/faculty/dashboard';
        } catch (error) {
            console.error('Error:', error);
            const msg = (window.getApiErrorMessage && window.getApiErrorMessage(error, 'Login failed. Please check your credentials.')) || (error && error.message) || 'Login failed. Please check your credentials.';

            showError(loginId, msg);
            showError(password, msg);
            loginId.focus();

            if (window.showToast) {
                window.showToast({ type: 'error', title: 'Invalid Login', message: msg });
            }
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
        }
    });
}

// Student Login Handler
if (document.getElementById('loginForm') && window.location.pathname.includes('/student/login')) {
    const form = document.getElementById('loginForm');
    const loginId = document.getElementById('loginId');
    const password = document.getElementById('password');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        clearValidationErrors();
        
        let isValid = true;

        if (loginId.value.trim() === '') {
            showError(loginId, 'Student ID is required');
            isValid = false;
        }

        if (password.value === '') {
            showError(password, 'Password is required');
            isValid = false;
        } else if (password.value.length < 6) {
            showError(password, 'Password must be at least 6 characters');
            isValid = false;
        }

        if (!isValid) return;

        const payload = {
            enrollment_no: loginId.value.trim(),
            password: password.value
        };

        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Logging in...';

        try {
            await apiPostJson(`${API_BASE_URL}/student/login`, payload);
            if (window.showToast) {
                window.showToast({ type: 'success', title: 'Login Successful', message: 'Welcome back.' });
            }
            window.location.href = '/student/dashboard';
        } catch (error) {
            console.error('Error:', error);
            const msg = (window.getApiErrorMessage && window.getApiErrorMessage(error, 'Login failed. Please check your credentials.')) || (error && error.message) || 'Login failed. Please check your credentials.';

            showError(loginId, msg);
            showError(password, msg);
            loginId.focus();

            if (window.showToast) {
                window.showToast({ type: 'error', title: 'Invalid Login', message: msg });
            }
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
        }
    });
}

// Helper Functions
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function showError(inputElement, message) {
    inputElement.classList.add('is-invalid');
    const errorDiv = inputElement.nextElementSibling;
    if (errorDiv && errorDiv.classList.contains('error-message')) {
        errorDiv.textContent = message;
        errorDiv.classList.add('show');
    }
}

function clearValidationErrors() {
    document.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
    document.querySelectorAll('.error-message').forEach(el => {
        el.textContent = '';
        el.classList.remove('show');
    });
}

function showSuccess(inputElement) {
    inputElement.classList.remove('is-invalid');
    inputElement.classList.add('is-valid');
}
