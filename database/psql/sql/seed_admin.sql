-- Seeds the admin row into `users` (database/psql/models/users.py).
-- Idempotent (ON CONFLICT DO NOTHING on the unique `login`) — safe to run on
-- every migration_restart, unlike user.sql which is superuser-only, one-time
-- role/database setup. Invoked by infra/scripts/database/restart.sh via the
-- app's own role, after migrations have created the `users` table.
--
-- The password below is a bcrypt hash (core/common/bcrypt_password.py) of
-- "haslo123@zaq1@WSX" — never store it in plaintext.

INSERT INTO users (id, login, password, type)
VALUES (
    gen_random_uuid(),
    'ChaLLengeR',
    '$2b$12$k6uR.01fub4SC1BAR74rFeqlEca7wfaRqpaZ8nwlAiB.yLfd6/Oqm',
    'admin'
)
ON CONFLICT (login) DO NOTHING;
