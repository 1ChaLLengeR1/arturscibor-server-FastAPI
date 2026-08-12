-- One-time setup, run manually as a Postgres superuser — NOT invoked by any
-- of the migration_*.sh scripts. Example:
--   sudo -u postgres psql -f database/psql/sql/user.sql
--
-- Adjust the role name/password/database name to match env/local.env (or
-- env/prod.env) before running, and change the password afterwards if you
-- ran this with the placeholder still in it.

CREATE ROLE arturscibor WITH LOGIN PASSWORD 'CHANGE_ME';
CREATE DATABASE arturscibor_portfolio OWNER arturscibor;
