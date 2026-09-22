-- Patch: add university profile fields
-- Safe to run multiple times (errors can be ignored if columns already exist)

ALTER TABLE universities ADD COLUMN registered_address TEXT NULL;
ALTER TABLE universities ADD COLUMN official_contact_email VARCHAR(150) NULL;
ALTER TABLE universities ADD COLUMN official_contact_phone VARCHAR(50) NULL;
ALTER TABLE universities ADD COLUMN website_url VARCHAR(255) NULL;
