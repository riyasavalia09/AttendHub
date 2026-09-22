-- Patch: allow Sunday in timetable day enum
-- Safe to run multiple times: will be a no-op if already includes SUN

ALTER TABLE timetable
MODIFY day ENUM('MON','TUE','WED','THU','FRI','SAT','SUN') NOT NULL;
