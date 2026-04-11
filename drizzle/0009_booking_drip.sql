-- Nurture drip: due-at set at insert; sent-at when Resend succeeds.
ALTER TABLE `bookings` ADD COLUMN `drip2_due_at` integer;
--> statement-breakpoint
ALTER TABLE `bookings` ADD COLUMN `drip2_sent_at` integer;
--> statement-breakpoint
ALTER TABLE `bookings` ADD COLUMN `drip3_due_at` integer;
--> statement-breakpoint
ALTER TABLE `bookings` ADD COLUMN `drip3_sent_at` integer;
