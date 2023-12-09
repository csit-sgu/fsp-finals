CREATE DATABASE fsp_finals;
\c fsp_finals

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE users (
    id uuid DEFAULT uuid_generate_v4 (),
    username varchar(128) UNIQUE NOT NULL,
    password bytea NOT NULL,
    is_admin boolean NOT NULL,
    passed_test boolean NOT NULL,
    is_subscriber boolean NOT NULL,
    birth_date timestamp NOT NULL,
    name varchar(128) NOT NULL,
    surname varchar(128) NOT NULL,
    weekly_goal real NOT NULL,

    PRIMARY KEY (id)
);

CREATE TABLE blocks (
    block_id uuid NOT NULL PRIMARY KEY,
    block_type varchar(128) NOT NULL,
    problem text NOT NULL,
    payload jsonb NOT NULL
);

CREATE TABLE quizzes (
    quiz_id uuid NOT NULL PRIMARY KEY,
    author_id uuid NOT NULL REFERENCES users(id),
    title varchar(256) NOT NULL,
    description TEXT NOT NULL,
    category varchar(128) NOT NULL,
    is_for_subs boolean NOT NULL,
    entry_id uuid NOT NULL REFERENCES blocks(block_id)
);

CREATE TABLE quiz_complexities (
    quiz_id uuid NOT NULL REFERENCES quizzes(quiz_id),
    age_group varchar(128) NOT NULL,
    complexity integer NOT NULL,

    PRIMARY KEY (quiz_id, age_group)
);

CREATE TABLE attempts (
    attempt_id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    quiz_id uuid NOT NULL REFERENCES quizzes(quiz_id),
    user_id uuid NOT NULL REFERENCES users(id),
    quiz_score real NOT NULL,
    time_passed bigint NOT NULL, -- in seconds
    start_timestamp timestamp NOT NULL
);

CREATE VIEW stats AS
    SELECT user_id, quiz_score, quiz_id, start_timestamp FROM attempts;

CREATE VIEW quiz_info AS
    SELECT q.quiz_id, q.author_id, q.title, 
           q.description, q.category, q.entry_id, 
           qc.age_group, qc.complexity 
    FROM quizzes AS q INNER JOIN quiz_complexities AS qc
    ON q.quiz_id = qc.quiz_id;
