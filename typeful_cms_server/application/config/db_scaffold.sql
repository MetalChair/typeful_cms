-- create table if not exists TYPEFUL_ROUTES (
--     id serial PRIMARY KEY NOT NULL,
--     query_name TEXT NOT NULL,
--     table_name TEXT NOT NULL
-- );
DROP SCHEMA IF exists public CASCADE;
DROP SCHEMA IF EXISTS attribs CASCADE;
create schema attribs;
create schema public;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
create table if not exists attribs."APP_DEFINITION" (
    id serial PRIMARY KEY NOT NULL,
    item_key TEXT not null,
    item_val TEXT not null
);
create table if not exists attribs."SCHEMA_ATTRIBS" (
    id serial PRIMARY KEY NOT NULL,
    table_name TEXT NOT NULL,
    child_tables TEXT[],
    parent_table TEXT
);
create table if not exists attribs."SCHEMA_PRIVACY" (
    id serial PRIMARY KEY NOT NULL,
    role_name TEXT,
    accesible_fields TEXT[],
    attrib_table_id INTEGER,
    CONSTRAINT fk_attrib_table_id 
        FOREIGN KEY(attrib_table_id) 
        REFERENCES attribs."SCHEMA_ATTRIBS"(id)  
);
create table if not exists attribs."MEDIA_RELATIONS" (
    id serial PRIMARY KEY NOT NULL,
    table_name TEXT,
    table_record_id UUID not null,
    media_record_id UUID not null
);

create table if not exists public."media" (
    id UUID DEFAULT uuid_generate_v4(),
    upload_date timestamp,
    url TEXT,
    name TEXT,
    tags TEXT[],
    accesible_to TEXT[]
);

GRANT ALL ON SCHEMA attribs TO typefulserver;
GRANT ALL ON SCHEMA public TO typefulserver;
insert into attribs."APP_DEFINITION" (item_key, item_val) VALUES ('APP_INIT','TRUE')