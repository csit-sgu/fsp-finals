CREATE DATABASE fsp_finals;
\c fsp_finals

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE users (
    id uuid DEFAULT uuid_generate_v4 (),
    username varchar(128) UNIQUE NOT NULL,
    password bytea NOT NULL,
    is_admin boolean NOT NULL,
    birth_date timestamp NOT NULL,
    name varchar(128) NOT NULL,
    surname varchar(128) NOT NULL,
    weekly_goal real NOT NULL,

    PRIMARY KEY (id)
);

CREATE TABLE blocks (
    block_id uuid NOT NULL PRIMARY KEY,
    block_type varchar(128) NOT NULL,
    payload jsonb NOT NULL
);

-- CREATE TABLE quiz_blocks (
--     block_id uuid,
--     quiz_id uuidm,
-- 
--     PRIMARY KEY (block_id, quiz_id)
-- )

CREATE TABLE quizzes (
    quiz_id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    author_id uuid NOT NULL REFERENCES users(id),
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

-- CREATE VIEW quiz_block_view AS 
--     SELECT block_id, block_type, payload, quiz_id, title, description, category
--     FROM quiz_blocks AS qb 
--         INNER JOIN quizzes AS q
--             ON q.quiz_id = qb.quiz_id
--         INNER JOIN blocks as b
--             ON qb.block_id = b.block_id;

INSERT INTO users (username, password, is_admin, birth_date, name, surname, weekly_score)
    VALUES ('aboba', 'aboba', '1', '1971-07-13', 'Michael', 'Chernigin', 69);