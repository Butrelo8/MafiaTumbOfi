-- Nullable lead ranking on bookings (computed at insert in app).
ALTER TABLE `bookings` ADD COLUMN `lead_score` integer;
--> statement-breakpoint
ALTER TABLE `bookings` ADD COLUMN `lead_priority` text;
