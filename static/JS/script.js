// Navbar scroll behavior
window.addEventListener('scroll', function() {
    const navbar = document.getElementById('mainNavbar');
    if (window.scrollY > 50) {
        navbar.classList.remove('transparent');
        navbar.classList.add('solid');
    } else {
        navbar.classList.remove('solid');
        navbar.classList.add('transparent');
    }

    // Update active nav link
    updateActiveNavLink();
});

// Initialize navbar state
document.addEventListener('DOMContentLoaded', function() {
    const navbar = document.getElementById('mainNavbar');
    if (window.scrollY > 50) {
        navbar.classList.add('solid');
    } else {
        navbar.classList.add('transparent');
    }
    updateActiveNavLink();
});

// Update active nav link based on scroll position
function updateActiveNavLink() {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link[href^="#"]');
    
    let current = '';
    
    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.clientHeight;
        if (window.scrollY >= (sectionTop - 200)) {
            current = section.getAttribute('id');
        }
    });

    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === '#' + current) {
            link.classList.add('active');
        }
    });
}

// Form validation functions
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePassword(password) {
    return password.length >= 8;
}

function showError(inputElement, message) {
    const errorDiv = inputElement.nextElementSibling;
    if (errorDiv && errorDiv.classList.contains('error-message')) {
        errorDiv.textContent = message;
        errorDiv.classList.add('show');
    }
    inputElement.classList.add('error');
    inputElement.classList.remove('success');
}

function showSuccess(inputElement) {
    const errorDiv = inputElement.nextElementSibling;
    if (errorDiv && errorDiv.classList.contains('error-message')) {
        errorDiv.classList.remove('show');
    }
    inputElement.classList.remove('error');
    inputElement.classList.add('success');
}

function clearValidation(inputElement) {
    const errorDiv = inputElement.nextElementSibling;
    if (errorDiv && errorDiv.classList.contains('error-message')) {
        errorDiv.classList.remove('show');
    }
    inputElement.classList.remove('error', 'success');
}

// Admin Signup Validation
if (document.getElementById('adminSignupForm')) {
    const form = document.getElementById('adminSignupForm');
    const universityName = document.getElementById('universityName');
    const adminName = document.getElementById('adminName');
    const email = document.getElementById('email');
    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('confirmPassword');

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        let isValid = true;

        // Validate university name
        if (universityName.value.trim() === '') {
            showError(universityName, 'University name is required');
            isValid = false;
        } else {
            showSuccess(universityName);
        }

        // Validate admin name
        if (adminName.value.trim() === '') {
            showError(adminName, 'Admin name is required');
            isValid = false;
        } else {
            showSuccess(adminName);
        }

        // Validate email
        if (email.value.trim() === '') {
            showError(email, 'Email is required');
            isValid = false;
        } else if (!validateEmail(email.value)) {
            showError(email, 'Please enter a valid email address');
            isValid = false;
        } else {
            showSuccess(email);
        }

        // Validate password
        if (password.value === '') {
            showError(password, 'Password is required');
            isValid = false;
        } else if (!validatePassword(password.value)) {
            showError(password, 'Password must be at least 8 characters');
            isValid = false;
        } else {
            showSuccess(password);
        }

        // Validate confirm password
        if (confirmPassword.value === '') {
            showError(confirmPassword, 'Please confirm your password');
            isValid = false;
        } else if (password.value !== confirmPassword.value) {
            showError(confirmPassword, 'Passwords do not match');
            isValid = false;
        } else {
            showSuccess(confirmPassword);
        }

        if (isValid) {
            if (typeof window.showToast === 'function') {
                window.showToast({ type: 'success', title: 'Validated', message: 'Form validation successful! Backend integration pending.' });
            }
            // form.reset();
        }
    });

    // Real-time validation
    [universityName, adminName, email, password, confirmPassword].forEach(input => {
        input.addEventListener('blur', function() {
            if (this.value.trim() !== '') {
                if (this === email && !validateEmail(this.value)) {
                    showError(this, 'Please enter a valid email address');
                } else if (this === password && !validatePassword(this.value)) {
                    showError(this, 'Password must be at least 8 characters');
                } else if (this === confirmPassword && this.value !== password.value) {
                    showError(this, 'Passwords do not match');
                } else {
                    showSuccess(this);
                }
            }
        });

        input.addEventListener('input', function() {
            if (this.classList.contains('error')) {
                clearValidation(this);
            }
        });
    });
}

// Login Form Validation (for all login pages)
if (document.getElementById('loginForm')) {
    const form = document.getElementById('loginForm');
    const loginId = document.getElementById('loginId');
    const password = document.getElementById('password');

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        let isValid = true;

        // Validate login ID
        if (loginId.value.trim() === '') {
            showError(loginId, 'Email/ID is required');
            isValid = false;
        } else {
            showSuccess(loginId);
        }

        // Validate password
        if (password.value === '') {
            showError(password, 'Password is required');
            isValid = false;
        } else {
            showSuccess(password);
        }

        if (isValid) {
            if (typeof window.showToast === 'function') {
                window.showToast({ type: 'success', title: 'Validated', message: 'Login validation successful! Backend authentication pending.' });
            }
            // form.reset();
        }
    });

    // Real-time validation
    [loginId, password].forEach(input => {
        input.addEventListener('blur', function() {
            if (this.value.trim() === '') {
                showError(this, this.placeholder + ' is required');
            } else {
                showSuccess(this);
            }
        });

        input.addEventListener('input', function() {
            if (this.classList.contains('error')) {
                clearValidation(this);
            }
        });
    });
}