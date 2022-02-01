-- create table if not exists TYPEFUL_ROUTES (
--     id serial PRIMARY KEY NOT NULL,
--     query_name TEXT NOT NULL,
--     table_name TEXT NOT NULL
-- );
DROP SCHEMA IF exists public CASCADE;
DROP SCHEMA IF EXISTS attribs CASCADE;
create schema attribs;
create schema public;
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


GRANT ALL ON SCHEMA attribs TO typefulserver;
GRANT ALL ON SCHEMA public TO typefulserver;
insert into attribs."APP_DEFINITION" (item_key, item_val) VALUES ('APP_INIT','TRUE')