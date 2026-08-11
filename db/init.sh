#!/bin/bash
# Entrypoint script: runs as part of docker-entrypoint-initdb.d on first container boot.
set -e

mysql -u root -p"${MYSQL_ROOT_PASSWORD}" <<-EOSQL
    CREATE DATABASE IF NOT EXISTS shortener_db
        CHARACTER SET utf8mb4
        COLLATE utf8mb4_unicode_ci;

    USE shortener_db;

    CREATE TABLE IF NOT EXISTS urls (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        short_code VARCHAR(20) NOT NULL UNIQUE,
        original_url TEXT NOT NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        expires_at DATETIME DEFAULT NULL,
        click_count BIGINT NOT NULL DEFAULT 0,
        INDEX idx_short_code (short_code)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

    -- url_app_user is already created by the MySQL entrypoint itself
    -- (via MYSQL_USER/MYSQL_PASSWORD env vars) with ALL PRIVILEGES by default.
    -- Tighten it here to only what the app needs.
    REVOKE ALL PRIVILEGES ON shortener_db.* FROM 'url_app_user'@'%';
    GRANT SELECT, INSERT, UPDATE ON shortener_db.* TO 'url_app_user'@'%';
    FLUSH PRIVILEGES;
EOSQL