-- create table if not exists TYPEFUL_ROUTES (
--     id serial PRIMARY KEY NOT NULL,
--     query_name TEXT NOT NULL,
--     table_name TEXT NOT NULL
-- );
create table if not exists "APP_DEFINITION" (
    id serial PRIMARY KEY NOT NULL,
    item_key TEXT not null,
    item_val TEXT not null
);
insert into "APP_DEFINITION" (item_key, item_val) VALUES ('APP_INIT','TRUE')