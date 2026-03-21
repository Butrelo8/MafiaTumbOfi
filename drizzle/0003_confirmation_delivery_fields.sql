ALTER TABLE bookings ADD COLUMN confirmation_last_error TEXT;
ALTER TABLE bookings ADD COLUMN confirmation_attempts INTEGER NOT NULL DEFAULT 1;

