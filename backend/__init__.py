# backend/__init__.py - Flask application factory
# This is where we set up the whole app: folders, secret key, error handlers,
# route imports, and the background DB initializer thread.

import os
import re
import threading

from flask import Flask, flash, redirect, request, url_for
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.security import check_password_hash, generate_password_hash

from database.db_config import get_db_connection


# figure out the project root so we can point Flask to the right folders
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MAX_PROFILE_PHOTO_SIZE = 10 * 1024 * 1024   # 10 MB hard limit for photos
MAX_PROFILE_PHOTO_SIZE_MB = MAX_PROFILE_PHOTO_SIZE // (1024 * 1024)


def _is_truthy(value: str) -> bool:
    """Quick helper - treats '1', 'true', 'yes', 'on' as True."""
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def ensure_admin_account():
    """Makes sure we always have an admin account ready on startup.
    If it already exists with the right password, we skip the update.
    Otherwise we create it or sync the credentials."""

    if not _is_truthy(os.environ.get("SYNC_ADMIN_ON_STARTUP", "true")):
        return

    # these can be overridden through env vars on the server
    admin_email = os.environ.get("DEFAULT_ADMIN_EMAIL", "admin@sobkaj.com").strip().lower()
    admin_password = os.environ.get("DEFAULT_ADMIN_PASSWORD", "Admin@123")
    admin_name = os.environ.get("DEFAULT_ADMIN_NAME", "Sobkaj Admin").strip() or "Sobkaj Admin"

    if not admin_email or not admin_password:
        return

    conn = get_db_connection()
    if conn is None:
        print("[ensure_admin] Warning: DB connection failed.")
        return

    try:
        # make sure the ENUM column includes 'admin' (handles older DB versions)
        migrate_cursor = conn.cursor()
        try:
            migrate_cursor.execute(
                "ALTER TABLE users MODIFY COLUMN role ENUM('customer', 'worker', 'admin') NOT NULL"
            )
            conn.commit()
        except Exception:
            pass
        finally:
            migrate_cursor.close()

        # check if admin already exists
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT user_id, full_name, password_hash
            FROM users
            WHERE email = %s AND role = 'admin'
            ORDER BY user_id DESC
            LIMIT 1
            """,
            (admin_email,),
        )
        admin_row = cursor.fetchone()
        cursor.close()

        if admin_row:
            # admin exists - check if name and password are already up to date
            current_name = (admin_row.get("full_name") or "").strip()
            current_hash = admin_row.get("password_hash") or ""
            password_matches = False
            if current_hash:
                try:
                    password_matches = check_password_hash(current_hash, admin_password)
                except Exception:
                    password_matches = False

            if current_name == admin_name and password_matches:
                conn.close()
                return  # nothing to do

            # name or password differ - sync them
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE users
                SET full_name = %s, password_hash = %s
                WHERE user_id = %s
                """,
                (admin_name, generate_password_hash(admin_password), admin_row["user_id"]),
            )
            conn.commit()
            cursor.close()
            conn.close()
            print("[ensure_admin] Admin credentials synchronized.")
            return

        # admin doesn't exist yet - insert fresh
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO users (full_name, email, password_hash, role, phone)
            VALUES (%s, %s, %s, 'admin', %s)
            """,
            (admin_name, admin_email, generate_password_hash(admin_password), None),
        )
        conn.commit()
        cursor.close()
        conn.close()
        print("[ensure_admin] Admin account created.")
    except Exception as e:
        conn.close()
        print(f"[ensure_admin] Warning: {e}")


def init_db():
    """Runs on startup in a background thread.
    Reads init_db.sql and executes each statement so the tables exist.
    Also patches any old commission values to match the current 5% rate."""

    sql_path = os.path.join(BASE_DIR, "database", "init_db.sql")
    if not os.path.exists(sql_path):
        return
    with open(sql_path, "r", encoding="utf-8") as f:
        raw = f.read()

    # strip SQL comments and split on semicolons
    clean = re.sub(r'--[^\n]*', '', raw)
    statements = [s.strip() for s in clean.split(";") if s.strip()]
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        for stmt in statements:
            # skip database-level commands (we already selected the DB in db_config)
            if stmt.upper().startswith("CREATE DATABASE") or stmt.upper().startswith("USE "):
                continue
            try:
                cursor.execute(stmt)
            except Exception:
                pass  # table likely already exists

        # fix any bookings stuck with the old 10% commission from earlier seeds
        try:
            from config import PLATFORM_COMMISSION_RATE
            cursor.execute(
                f"UPDATE bookings SET platform_commission = ROUND(total_amount * {PLATFORM_COMMISSION_RATE}, 2) "
                f"WHERE platform_commission != ROUND(total_amount * {PLATFORM_COMMISSION_RATE}, 2)"
            )
            conn.commit()
        except Exception as e:
            print(f"[init_db - commission update] Warning: {e}")
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"[init_db] Warning: {e}")

    ensure_admin_account()


def create_app():
    """Factory function - builds and returns the configured Flask app."""

    app = Flask(
        __name__,
        template_folder=os.path.join(BASE_DIR, "frontend", "templates"),
        static_folder=os.path.join(BASE_DIR, "frontend", "static"),
    )
    app.secret_key = os.environ.get("SECRET_KEY", "sobkaj_secret_key_change_me")

    app.config["UPLOAD_FOLDER"] = os.path.join(BASE_DIR, "frontend", "static", "uploads")
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB max upload

    @app.errorhandler(RequestEntityTooLarge)
    def handle_request_entity_too_large(_error):
        flash(
            f"Upload is too large. Profile pictures must be {MAX_PROFILE_PHOTO_SIZE_MB} MB or smaller.",
            "warning",
        )
        return redirect(request.referrer or url_for("profile_setup"))

    # pull in all route blueprints
    from backend.routes import register_all_routes
    register_all_routes(app)

    # run DB setup in background so the server starts immediately
    threading.Thread(target=init_db, daemon=True).start()

    return app
