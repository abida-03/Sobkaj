# db_config.py - MySQL connection setup
# Checks for cloud database URLs first (Azure, Railway), falls back to local XAMPP.
# We use mysql-connector-python directly - no ORM, all SQL is written by hand.

import os
from urllib.parse import urlparse, unquote

import mysql.connector
from mysql.connector import Error


def _build_db_config() -> dict:
    """Figures out which database to connect to.
    On the server, we read MYSQL_URL or JAWSDB_URL from env vars.
    Locally, we just connect to XAMPP's MySQL with default settings."""

    dsn = os.environ.get("MYSQL_URL") or os.environ.get("JAWSDB_URL")

    if dsn:
        # parse the DSN string like mysql://user:pass@host:3306/dbname
        parsed = urlparse(dsn)
        cfg = {
            "host":     parsed.hostname,
            "user":     unquote(parsed.username or ""),
            "password": unquote(parsed.password or ""),
            "database": parsed.path.lstrip("/"),
            "port":     parsed.port or 3306,
        }
        # Azure MySQL requires SSL
        if parsed.hostname and "azure.com" in parsed.hostname:
            cfg["ssl_disabled"] = False
        return cfg

    # local development with XAMPP
    return {
        "host":     "localhost",
        "user":     "root",
        "password": "",
        "database": "sobkaj",
    }


DB_CONFIG = _build_db_config()


def get_db_connection():
    """Opens a fresh MySQL connection. The caller must close it when done.

    Usage:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
    """
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"[DB ERROR] Failed to connect to MySQL: {e}")
        return None
