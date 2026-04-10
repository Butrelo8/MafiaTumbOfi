-- Rebuild bookings so confirmation_attempts uses DEFAULT 0 (matches app insert semantics).
-- SQLite cannot ALTER COLUMN default in place.
CREATE TABLE `bookings_new` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`name` text NOT NULL,
	`email` text NOT NULL,
	`phone` text,
	`event_date` text,
	`city` text,
	`event_type` text,
	`duration` text,
	`show_type` text,
	`attendees` text,
	`venue_sound` text,
	`budget` text,
	`message` text,
	`status` text NOT NULL DEFAULT 'pending',
	`confirmation_last_error` text,
	`confirmation_attempts` integer NOT NULL DEFAULT 0,
	`created_at` integer
);
--> statement-breakpoint
INSERT INTO `bookings_new` SELECT `id`, `name`, `email`, `phone`, `event_date`, `city`, `event_type`, `duration`, `show_type`, `attendees`, `venue_sound`, `budget`, `message`, `status`, `confirmation_last_error`, `confirmation_attempts`, `created_at` FROM `bookings`;
--> statement-breakpoint
DROP TABLE `bookings`;
--> statement-breakpoint
ALTER TABLE `bookings_new` RENAME TO `bookings`;
