-- DESTRUCTIVE. Drops every table this project owns, plus Alembic's own
-- version table, so the schema can be rebuilt from scratch. Child tables
-- (the ones with a ForeignKey) are dropped before their parents, though
-- CASCADE would handle the ordering either way.

-- Current schema (docs/3.4-*, docs/3.5-projects-section.md, docs/6-file-storage-section-done.md).
DROP TABLE IF EXISTS project_images CASCADE;
DROP TABLE IF EXISTS about_me_images CASCADE;
DROP TABLE IF EXISTS tools_images CASCADE;
DROP TABLE IF EXISTS work_items CASCADE;
DROP TABLE IF EXISTS work CASCADE;
DROP TABLE IF EXISTS curriculum_vitae CASCADE;
DROP TABLE IF EXISTS about_me CASCADE;
DROP TABLE IF EXISTS tools CASCADE;
DROP TABLE IF EXISTS contact CASCADE;
DROP TABLE IF EXISTS projects CASCADE;
DROP TABLE IF EXISTS files CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Pre-rework table names — dropped by earlier migrations already, kept here
-- (IF EXISTS, so harmless) in case this runs against a database that never
-- got that far.
DROP TABLE IF EXISTS readmore CASCADE;
DROP TABLE IF EXISTS aboutme CASCADE;
DROP TABLE IF EXISTS informationme CASCADE;
DROP TABLE IF EXISTS imagesme CASCADE;
DROP TABLE IF EXISTS jobs CASCADE;
DROP TABLE IF EXISTS curriculumvitae CASCADE;
DROP TABLE IF EXISTS filesproject CASCADE;
DROP TABLE IF EXISTS imagesproject CASCADE;
DROP TABLE IF EXISTS technologiesproject CASCADE;

DROP TABLE IF EXISTS alembic_version CASCADE;

-- Enum types are standalone objects, not owned by any table — DROP TABLE
-- never removes them, so they survive a restart and collide with the next
-- CREATE TYPE (see database/psql/models/{file,work,projects}.py for the source enums).
DROP TYPE IF EXISTS file_type CASCADE;
DROP TYPE IF EXISTS file_status CASCADE;
DROP TYPE IF EXISTS employment_type CASCADE;
DROP TYPE IF EXISTS project_level CASCADE;
