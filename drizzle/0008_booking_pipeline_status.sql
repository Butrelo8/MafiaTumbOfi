-- Sales follow-up state (orthogonal to email confirmation `status`).
ALTER TABLE `bookings` ADD COLUMN `pipeline_status` text NOT NULL DEFAULT 'new';
