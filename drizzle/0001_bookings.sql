CREATE TABLE `bookings` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`name` text NOT NULL,
	`email` text NOT NULL,
	`phone` text,
	`event_date` text,
	`message` text,
	`status` text NOT NULL DEFAULT 'pending',
	`created_at` integer
);
