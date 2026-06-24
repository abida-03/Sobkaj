# auth.py - handles registration, OTP verification, login, and logout
# This is the first thing a user interacts with when they visit Sobkaj.

import os

from flask import render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

from database.db_config import get_db_connection
from backend.email_utils import generate_otp, send_otp_email


def _sync_default_admin_credentials(conn):
    """Makes sure the default admin account matches what's in the env vars.
    Called during login so the admin can always get in, even if the DB
    was reset or migrated."""

    admin_email = os.environ.get("DEFAULT_ADMIN_EMAIL", "admin@sobkaj.com").strip().lower()
    admin_password = os.environ.get("DEFAULT_ADMIN_PASSWORD", "Admin@123")
    admin_name = os.environ.get("DEFAULT_ADMIN_NAME", "Sobkaj Admin").strip() or "Sobkaj Admin"

    if not admin_email or not admin_password:
        return

    # make sure the role ENUM includes 'admin'
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

    # look up existing admin
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
        # admin exists - see if credentials need updating
        current_name = (admin_row.get("full_name") or "").strip()
        current_hash = admin_row.get("password_hash") or ""
        password_matches = False
        if current_hash:
            try:
                password_matches = check_password_hash(current_hash, admin_password)
            except Exception:
                password_matches = False

        if current_name == admin_name and password_matches:
            return  # already synced

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
        return

    # no admin found - create one
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


def register_auth_routes(app):

    # ---- Landing Page ----

    @app.route("/")
    def index():
        return render_template("index.html")

    # ---- Registration Flow ----

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            full_name = request.form.get("full_name", "").strip()
            email     = request.form.get("email", "").strip()
            phone     = request.form.get("phone", "").strip()
            password  = request.form.get("password", "")
            confirm   = request.form.get("confirm_password", "")
            role      = request.form.get("role", "customer").strip().lower()

            if role not in ("customer", "worker"):
                role = "customer"

            if not full_name or not email or not password:
                flash("Please fill in all required fields.", "danger")
                return redirect(url_for("register"))

            if password != confirm:
                flash("Passwords do not match.", "danger")
                return redirect(url_for("register"))

            # check for duplicate email+role combination
            conn = get_db_connection()
            if conn is None:
                flash("Database connection failed.", "danger")
                return redirect(url_for("register"))

            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT user_id FROM users WHERE email = %s AND role = %s",
                (email, role),
            )
            existing = cursor.fetchone()
            cursor.close()
            conn.close()

            if existing:
                flash(f"A {role} account with this email already exists.", "warning")
                return redirect(url_for("register"))

            # send OTP email before creating the account
            otp = generate_otp()
            if not send_otp_email(email, otp):
                flash("Failed to send OTP email. Check your Gmail settings.", "danger")
                return redirect(url_for("register"))

            # stash registration data in session until OTP is verified
            session["reg_full_name"] = full_name
            session["reg_email"]     = email
            session["reg_phone"]     = phone
            session["reg_password"]  = generate_password_hash(password)
            session["reg_role"]      = role
            session["reg_otp"]       = otp

            flash("A verification code has been sent to your email.", "info")
            return redirect(url_for("verify_otp"))

        return render_template("register.html")

    # ---- OTP Verification ----

    @app.route("/verify_otp", methods=["GET", "POST"])
    def verify_otp():
        # can't verify if they haven't started registration
        if "reg_otp" not in session:
            flash("Please register first.", "warning")
            return redirect(url_for("register"))

        if request.method == "POST":
            entered_otp = request.form.get("otp", "").strip()

            if entered_otp == session.get("reg_otp"):
                conn = get_db_connection()
                if conn is None:
                    flash("Database connection failed.", "danger")
                    return redirect(url_for("verify_otp"))

                cursor = None
                try:
                    # double-check nobody registered while we were verifying
                    cursor = conn.cursor(dictionary=True)
                    cursor.execute(
                        "SELECT user_id FROM users WHERE email = %s AND role = %s",
                        (session["reg_email"], session["reg_role"]),
                    )
                    if cursor.fetchone():
                        cursor.close()
                        conn.close()
                        for key in list(session.keys()):
                            if key.startswith("reg_"):
                                session.pop(key)
                        flash("This account already exists. Please log in.", "info")
                        return redirect(url_for("login"))

                    # OTP matched and no duplicate - create the account
                    cursor.close()
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO users (full_name, email, password_hash, role, phone)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        session["reg_full_name"],
                        session["reg_email"],
                        session["reg_password"],
                        session["reg_role"],
                        session["reg_phone"],
                    ))
                    conn.commit()
                    cursor.close()
                    conn.close()

                    # clean up session
                    for key in list(session.keys()):
                        if key.startswith("reg_"):
                            session.pop(key)

                    flash("Account created successfully! Please log in.", "success")
                    return redirect(url_for("login"))

                except Exception as e:
                    conn.rollback()
                    if cursor is not None:
                        cursor.close()
                    conn.close()
                    if "Duplicate entry" in str(e):
                        for key in list(session.keys()):
                            if key.startswith("reg_"):
                                session.pop(key)
                        flash("An account with this email and role already exists.", "warning")
                        return redirect(url_for("login"))
                    flash(f"Registration failed: {e}", "danger")
                    return redirect(url_for("verify_otp"))
            else:
                flash("Invalid OTP. Please try again.", "danger")
                return redirect(url_for("verify_otp"))

        return render_template("verify_otp.html")

    # ---- Login ----

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email    = request.form.get("email", "").strip()
            password = request.form.get("password", "")
            requested_role = request.form.get("role", "").strip().lower()

            if not email or not password:
                flash("Please fill in all fields.", "danger")
                return redirect(url_for("login"))

            conn = get_db_connection()
            if conn is None:
                flash("Database connection failed.", "danger")
                return redirect(url_for("login"))

            # if someone is trying to log in as admin, make sure the account is synced
            default_admin_email = os.environ.get("DEFAULT_ADMIN_EMAIL", "admin@sobkaj.com").strip().lower()
            if requested_role == "admin" or email.lower() == default_admin_email:
                try:
                    _sync_default_admin_credentials(conn)
                except Exception as e:
                    print(f"[login-admin-sync] Warning: {e}")

            cursor = conn.cursor(dictionary=True)

            # fetch user(s) matching the email (and optionally role)
            if requested_role in ("customer", "worker", "admin"):
                cursor.execute("""
                    SELECT user_id, full_name, email, password_hash, role
                    FROM users WHERE email = %s AND role = %s
                    ORDER BY user_id DESC
                """, (email, requested_role))
            else:
                cursor.execute("""
                    SELECT user_id, full_name, email, password_hash, role
                    FROM users WHERE email = %s
                    ORDER BY user_id DESC
                """, (email,))

            candidates = cursor.fetchall()
            cursor.close()
            conn.close()

            # try each candidate until we find one whose password matches
            user = None
            for candidate in candidates:
                if check_password_hash(candidate["password_hash"], password):
                    user = candidate
                    break

            if user:
                # set up the session so other routes know who's logged in
                session["user_id"]   = user["user_id"]
                session["full_name"] = user["full_name"]
                session["email"]     = user["email"]
                session["role"]      = user["role"]

                flash(f"Welcome back, {user['full_name']}!", "success")

                # redirect to the right dashboard based on role
                if user["role"] == "worker":
                    return redirect(url_for("worker_dashboard"))
                elif user["role"] == "admin":
                    return redirect(url_for("admin_dashboard"))
                else:
                    return redirect(url_for("customer_dashboard"))
            else:
                # fallback for admin when the DB might be temporarily out of sync
                default_admin_password = os.environ.get("DEFAULT_ADMIN_PASSWORD", "Admin@123")
                default_admin_name = os.environ.get("DEFAULT_ADMIN_NAME", "Sobkaj Admin").strip() or "Sobkaj Admin"

                if (
                    (requested_role == "admin" or email.lower() == default_admin_email)
                    and email.lower() == default_admin_email
                    and password == default_admin_password
                ):
                    session["user_id"] = 0
                    session["full_name"] = default_admin_name
                    session["email"] = default_admin_email
                    session["role"] = "admin"
                    flash(f"Welcome back, {default_admin_name}!", "success")
                    return redirect(url_for("admin_dashboard"))

                if requested_role in ("customer", "worker") and not candidates:
                    flash(f"No {requested_role} account was found for this email.", "warning")
                    return redirect(url_for("login"))
                flash("Invalid email or password.", "danger")
                return redirect(url_for("login"))

        return render_template("login.html")

    # ---- Logout ----

    @app.route("/logout")
    def logout():
        session.clear()
        flash("You have been logged out.", "info")
        return redirect(url_for("login"))
