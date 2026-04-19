ALTER TABLE bookings ADD COLUMN confirmation_last_error TEXT;
--> statement-breakpoint
ALTER TABLE bookings ADD COLUMN confirmation_attempts INTEGER NOT NULL DEFAULT 1;

