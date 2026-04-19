-- Operator soft-delete: hidden from admin/export/drip until restored via SQL.
ALTER TABLE `bookings` ADD COLUMN `deleted_at` integer;
