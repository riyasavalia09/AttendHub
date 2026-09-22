-- Analytics performance indexes (safe to run multiple times if indexes do not already exist)
-- Note: MySQL doesn't support IF NOT EXISTS for indexes in older versions.
-- Run manually and ignore "Duplicate key name" if already created.

-- Fast lecture lookups from attendance
ALTER TABLE attendance
  ADD INDEX idx_attendance_lecture (lecture_id);

-- Fast joining lectures -> timetable
ALTER TABLE lectures
  ADD INDEX idx_lectures_timetable (timetable_id);

-- Common filtering/grouping dimensions
ALTER TABLE timetable
  ADD INDEX idx_timetable_university (university_id),
  ADD INDEX idx_timetable_department_semester (department, semester),
  ADD INDEX idx_timetable_subject (subject);

-- Optional: speed up student filtering
ALTER TABLE students
  ADD INDEX idx_students_department_semester (department, semester),
  ADD INDEX idx_students_university_department_semester (university_id, department, semester);
