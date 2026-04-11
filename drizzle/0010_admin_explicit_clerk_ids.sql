-- One-time alignment for known accounts (idempotent UPDATEs).
UPDATE "users" SET "is_admin" = 1 WHERE "clerk_id" = 'user_3CCb0fWe0Kc6EJkcpUwGW8Hl5Ec';
UPDATE "users" SET "is_admin" = 0 WHERE "clerk_id" = 'user_3CE9N7hn5rXEdsBDXXYwBeJTez7';
