-- DESTRUCTIVE. Drops every table this project owns, plus Alembic's own
-- version table, so the schema can be rebuilt from scratch. Child tables
-- (the ones with a ForeignKey) are dropped before their parents, though
-- CASCADE would handle the ordering either way.

DROP TABLE IF EXISTS filesproject CASCADE;
DROP TABLE IF EXISTS imagesproject CASCADE;
DROP TABLE IF EXISTS technologiesproject CASCADE;
DROP TABLE IF EXISTS projects CASCADE;
DROP TABLE IF EXISTS contact CASCADE;
DROP TABLE IF EXISTS tools CASCADE;
DROP TABLE IF EXISTS readmore CASCADE;
DROP TABLE IF EXISTS aboutme CASCADE;
DROP TABLE IF EXISTS informationme CASCADE;
DROP TABLE IF EXISTS imagesme CASCADE;
DROP TABLE IF EXISTS jobs CASCADE;
DROP TABLE IF EXISTS curriculumvitae CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS alembic_version CASCADE;
