
-- 8. Reports Table
CREATE TABLE IF NOT EXISTS reports (
    report_id INT AUTO_INCREMENT PRIMARY KEY,
    university_id INT NOT NULL,
    report_type VARCHAR(100) NOT NULL, -- 'Attendance Summary', 'Faculty Performance', etc.
    generated_by VARCHAR(100) NOT NULL, -- 'System', 'Admin'
    coverage_period VARCHAR(100), -- 'Last 30 Days', 'Fall 2023', etc.
    file_path VARCHAR(255), -- Virtual or real path to PDF/CSV
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (university_id) REFERENCES universities(university_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
