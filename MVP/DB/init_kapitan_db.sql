CREATE DATABASE IF NOT EXISTS kapitan_db;

USE kapitan_db;

CREATE TABLE IF NOT EXISTS users(
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    firstname VARCHAR(50),
    lastname VARCHAR(50),
    email VARCHAR(128),
    username VARCHAR(30),
    password_sha256_hexdigest VARCHAR(64),
    salt VARCHAR(2)
);

CREATE TABLE IF NOT EXISTS scripts(
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(120),
    description VARCHAR(220),
    upload_at DATETIME,
    user_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS images(
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(120),
    description VARCHAR(220),
    upload_at DATETIME,
    user_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS projects(
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120),
    description VARCHAR(250),
    user_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS servers(
    sid VARCHAR(60), 
    project_id INTEGER,
    join_date DATETIME,
    FOREIGN KEY (project_id) REFERENCES projects(id),
    PRIMARY KEY (sid, project_id)
);

CREATE TABLE IF NOT EXISTS tasks(
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    project_id INT, 
    server_id VARCHAR(60),
    task_json TEXT,
    completed BOOLEAN DEFAULT 0,
    FOREIGN KEY (server_id) REFERENCES servers(sid),
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

CREATE TABLE IF NOT EXISTS images_servers(
    image_id INTEGER,
    user_id INTEGER,
    server_id VARCHAR(60),
    project_id INTEGER,
    PRIMARY KEY (image_id, server_id, project_id),
    FOREIGN KEY (image_id) REFERENCES images(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (server_id) REFERENCES servers(sid),
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

CREATE TABLE IF NOT EXISTS scripts_servers(
    script_id INTEGER,
    user_id INTEGER,
    server_id VARCHAR(60),
    project_id INTEGER,
    PRIMARY KEY (script_id, server_id, project_id),
    FOREIGN KEY (script_id) REFERENCES scripts(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (server_id) REFERENCES servers(sid),
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

CREATE TABLE IF NOT EXISTS tasks_feedback(
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    task_id INTEGER,
    task_feedback TEXT NOT NULL,
    posted_at DATETIME,
    FOREIGN KEY (task_id) REFERENCES tasks(id)
);

CREATE TABLE IF NOT EXISTS servers_feedback(
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    feedback TEXT,
    posted_at DATETIME,
    project_id INT,
    server_id VARCHAR(60),
    FOREIGN KEY (server_id) REFERENCES servers(sid),
    FOREIGN KEY (project_id) REFERENCES projects(id)
);