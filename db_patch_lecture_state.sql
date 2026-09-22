-- Align lecture status model with attendance workflow.
ALTER TABLE lectures
MODIFY COLUMN status ENUM('NOT_STARTED', 'ONGOING', 'MARKED', 'ENDED') DEFAULT 'NOT_STARTED';

-- Ensure DB-level protection against duplicate attendance rows.
SET @attendance_unique_exists := (
    SELECT COUNT(*)
    FROM information_schema.statistics
    WHERE table_schema = DATABASE()
      AND table_name = 'attendance'
      AND index_name = 'unique_attendance'
);

SET @attendance_unique_sql := IF(
    @attendance_unique_exists = 0,
    'ALTER TABLE attendance ADD CONSTRAINT unique_attendance UNIQUE (lecture_id, student_id)',
    'SELECT 1'
);

PREPARE attendance_stmt FROM @attendance_unique_sql;
EXECUTE attendance_stmt;
DEALLOCATE PREPARE attendance_stmt;
