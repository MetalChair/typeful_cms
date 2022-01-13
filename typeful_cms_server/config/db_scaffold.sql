create table if not exists typeful_routes (
    id serial PRIMARY KEY NOT NULL,
    route TEXT NOT NULL,
    name TEXT NOT NULL,
    tabel_name TEXT NOT NULL,
    model_def TEXT
);
create table if not exists app_definition (
    id serial PRIMARY KEY NOT NULL,
    item_key TEXT not null,
    item_val TEXT not null
);

insert into app_definition (item_key, item_val) VALUES ('APP_INIT','TRUE')