create table typeful_routes (
    id INT PRIMARY KEY NOT NULL,
    route TEXT NOT NULL,
    schema TEXT NOT NULL,
    return TEXT
);
create table app_definition (
    id INT PRIMARY KEY NOT NULL,
    item_key TEXT not null,
    item_val TEXT not null
);