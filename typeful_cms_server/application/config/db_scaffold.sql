-- create table if not exists TYPEFUL_ROUTES (
--     id serial PRIMARY KEY NOT NULL,
--     query_name TEXT NOT NULL,
--     table_name TEXT NOT NULL
-- );
create schema attribs;
create schema public;
create table if not exists attribs."APP_DEFINITION" (
    id serial PRIMARY KEY NOT NULL,
    item_key TEXT not null,
    item_val TEXT not null
);
create table if not exists attribs."SCHEMA_PRIVACY" (
    id serial PRIMARY KEY NOT NULL,
    public TEXT[],
    table_id INTEGER FOREIGN KEY
);

GRANT ALL ON SCHEMA attribs TO typefulserver;
GRANT ALL ON SCHEMA public TO typefulserver;
insert into attribs."APP_DEFINITION" (item_key, item_val) VALUES ('APP_INIT','TRUE')