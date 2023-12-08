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
    block_id uuid NOT NULL PRIMARY KEY,
    author_id uuid NOT NULL REFERENCES users(id),
    block_type varchar(128) NOT NULL,
    payload jsonb NOT NULL
);

CREATE TABLE quizzes (
    quiz_id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    title varchar(256) NOT NULL,
    description TEXT NOT NULL,
    category varchar(128) NOT NULL,
    entry_id uuid NOT NULL REFERENCES blocks(block_id)
);

CREATE TABLE quiz_complexities (
    quiz_id bigint NOT NULL REFERENCES quizzes(quiz_id),
    age_group varchar(128) NOT NULL,
    complexity varchar(128) NOT NULL,

    PRIMARY KEY (quiz_id, age_group)
);

CREATE TABLE attempts (
    attempt_id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    quiz_id bigint NOT NULL REFERENCES quizzes(quiz_id),
    user_id uuid NOT NULL REFERENCES users(id),
    quiz_score real NOT NULL,
    time_passed bigint NOT NULL, -- in seconds
    start_timestamp timestamp NOT NULL
);

CREATE TABLE running_containers (
    container_id varchar(64) UNIQUE NOT NULL,
    user_id uuid NOT NULL REFERENCES users(id),
    block_id uuid NOT NULL REFERENCES blocks(block_id),
    host_ip varchar(32) NOT NULL,
    host_port varchar(10) NOT NULL,
    start_timestamp timestamp NOT NULL
);
