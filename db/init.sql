CREATE DATABASE fsp_finals;
\c fsp_finals

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE users (
    id uuid DEFAULT uuid_generate_v4 (),
    username varchar(128) UNIQUE NOT NULL,
    password bytea NOT NULL,
    is_admin boolean NOT NULL,
    birthdate timestamp NOT NULL,
    name varchar(128) NOT NULL,
    surname varchar(128) NOT NULL,
    weekly_score real NOT NULL,

    PRIMARY KEY (id)
);

CREATE TABLE blocks (
    block_id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    author_id uuid NOT NULL REFERENCES users(id),
    block_type varchar(128) NOT NULL,
    payload jsonb NOT NULL
);

CREATE TABLE tasks (
    task_id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    category varchar(128) NOT NULL,
    entry_id bigint NOT NULL REFERENCES blocks(block_id)
);

CREATE TABLE task_complexities (
    task_id bigint NOT NULL REFERENCES tasks(task_id),
    age_group varchar(128) NOT NULL,
    complexity varchar(128) NOT NULL,

    PRIMARY KEY (task_id, age_group)
);

CREATE TABLE attempts (
    attempt_id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    task_id bigint NOT NULL REFERENCES tasks(task_id),
    user_id uuid NOT NULL REFERENCES users(id),
    task_score real NOT NULL,
    time_passed bigint NOT NULL, -- in seconds
    start_timestamp timestamp NOT NULL
);

CREATE TABLE running_containers (
    container_id varchar(64) UNIQUE NOT NULL,
    user_id uuid NOT NULL REFERENCES users(id),
    block_id bigint NOT NULL REFERENCES blocks(block_id),
    host_ip varchar(32) NOT NULL,
    host_port varchar(10) NOT NULL,
    start_timestamp timestamp NOT NULL
);
