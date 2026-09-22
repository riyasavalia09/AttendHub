-- Password reset tokens (for forgot/reset password flow)

CREATE TABLE IF NOT EXISTS password_reset_tokens (
    token_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    role ENUM('admin', 'faculty', 'student') NOT NULL,
    user_id INT NOT NULL,
    university_id INT NULL,
    token_hash CHAR(64) NOT NULL,
    expires_at DATETIME NOT NULL,
    used_at DATETIME NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_password_reset_token_hash (token_hash),
    INDEX idx_password_reset_role_user (role, user_id),
    INDEX idx_password_reset_expires (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
