CREATE TABLE `tour_dates` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`date` text NOT NULL,
	`time` text,
	`city` text NOT NULL,
	`venue` text NOT NULL,
	`status` text DEFAULT 'confirmed' NOT NULL,
	`ticket_url` text,
	`sold_out` integer DEFAULT false NOT NULL,
	`internal_notes` text,
	`created_at` integer,
	`updated_at` integer
);
