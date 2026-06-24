# worker.py - all routes related to the worker side of Sobkaj
# Dashboard, profile setup, profile editing, NID verification,
# BRAC training, skill management, booking updates, and public profile.

from flask import render_template, request, redirect, url_for, session, flash, jsonify

from database.db_config import get_db_connection
from backend.helpers import (
    DUMMY_NID_DATABASE,
    save_profile_photo,
    get_background_verification_sql,
)


def register_worker_routes(app):

    # ---- Worker Dashboard ----

    @app.route("/worker/dashboard")
    def worker_dashboard():
        if "user_id" not in session or session.get("role") != "worker":
            flash("Please log in as a worker.", "warning")
            return redirect(url_for("login"))

        user_id = session["user_id"]
        conn = get_db_connection()
        if conn is None:
            flash("Database connection failed.", "danger")
            return redirect(url_for("login"))

        cursor = conn.cursor(dictionary=True)
        verification_select, _ = get_background_verification_sql(cursor)

        # load worker profile joined with user info
        cursor.execute(f"""
            SELECT wp.*, {verification_select}, u.full_name, u.email, u.phone
            FROM worker_profiles wp
            JOIN users u ON u.user_id = wp.user_id
            WHERE wp.user_id = %s
        """, (user_id,))
        profile = cursor.fetchone()

        if not profile:
            cursor.close()
            conn.close()
            flash("Please complete your profile setup first.", "info")
            return redirect(url_for("profile_setup"))

        # skills this worker already has
        cursor.execute("""
            SELECT s.skill_id, s.skill_name
            FROM worker_skills ws
            JOIN skills s ON s.skill_id = ws.skill_id
            WHERE ws.worker_id = %s
        """, (user_id,))
        my_skills = cursor.fetchall()

        # skills they haven't added yet (uses NOT IN subquery)
        cursor.execute("""
            SELECT s.skill_id, s.skill_name FROM skills s
            WHERE s.skill_id NOT IN (
                SELECT ws.skill_id FROM worker_skills ws WHERE ws.worker_id = %s
            )
        """, (user_id,))
        available_skills = cursor.fetchall()

        # all bookings for this worker, sorted by status priority then date
        cursor.execute("""
            SELECT b.booking_id, b.service_date, b.service_time, b.hours_requested,
                   b.total_amount, b.platform_commission, b.status,
                   u.full_name AS customer_name, u.phone AS customer_phone
            FROM bookings b
            INNER JOIN users u ON u.user_id = b.customer_id
            WHERE b.worker_id = %s
            ORDER BY
                FIELD(b.status, 'pending', 'confirmed', 'completed', 'cancelled'),
                b.service_date ASC, b.service_time ASC
        """, (user_id,))
        bookings = cursor.fetchall()

        # aggregate rating stats for the dashboard summary
        cursor.execute("""
            SELECT
                COUNT(*)                                               AS rating_count,
                ROUND(AVG(stars), 1)                                   AS avg_rating,
                COUNT(CASE WHEN review_text IS NOT NULL THEN 1 END)    AS review_count
            FROM ratings WHERE worker_id = %s
        """, (user_id,))
        rating_stats = cursor.fetchone()

        cursor.close()
        conn.close()

        return render_template("worker_dashboard.html",
                               profile=profile,
                               my_skills=my_skills,
                               available_skills=available_skills,
                               bookings=bookings,
                               rating_stats=rating_stats)

    # ---- Booking Status Updates ----

    @app.route("/update_booking_status", methods=["POST"])
    def update_booking_status():
        """Worker can accept, reject, or mark a booking as completed."""

        if "user_id" not in session or session.get("role") != "worker":
            flash("Please log in as a worker.", "warning")
            return redirect(url_for("login"))

        booking_id = request.form.get("booking_id")
        new_status = request.form.get("new_status")

        if new_status not in ("confirmed", "cancelled", "completed"):
            flash("Invalid status.", "danger")
            return redirect(url_for("worker_dashboard"))

        conn = get_db_connection()
        if conn is None:
            flash("Database connection failed.", "danger")
            return redirect(url_for("worker_dashboard"))

        try:
            cursor = conn.cursor()
            # WHERE worker_id check ensures workers can only update their own bookings
            cursor.execute("""
                UPDATE bookings SET status = %s
                WHERE booking_id = %s AND worker_id = %s
            """, (new_status, int(booking_id), session["user_id"]))
            conn.commit()
            cursor.close()
            conn.close()

            labels = {"confirmed": "accepted", "cancelled": "rejected", "completed": "marked as completed"}
            flash(f"Booking #{booking_id} {labels.get(new_status, new_status)}.", "success")
        except Exception as e:
            conn.rollback()
            cursor.close()
            conn.close()
            flash(f"Failed to update booking: {e}", "danger")

        return redirect(url_for("worker_dashboard"))

    # ---- Availability Toggle ----

    @app.route("/update_availability", methods=["POST"])
    def update_availability():
        """Worker sets themselves as available, busy, or offline."""

        if "user_id" not in session or session.get("role") != "worker":
            flash("Please log in as a worker.", "warning")
            return redirect(url_for("login"))

        new_status = request.form.get("availability_status")
        if new_status not in ("available", "busy", "offline"):
            flash("Invalid availability status.", "danger")
            return redirect(url_for("worker_dashboard"))

        conn = get_db_connection()
        if conn is None:
            flash("Database connection failed.", "danger")
            return redirect(url_for("worker_dashboard"))

        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE worker_profiles SET availability_status = %s WHERE user_id = %s
            """, (new_status, session["user_id"]))
            conn.commit()
            cursor.close()
            conn.close()
            flash(f"Availability updated to '{new_status}'.", "success")
        except Exception as e:
            conn.rollback()
            cursor.close()
            conn.close()
            flash(f"Failed to update availability: {e}", "danger")

        return redirect(url_for("worker_dashboard"))

    # ---- Bio Update ----

    @app.route("/update_bio", methods=["POST"])
    def update_bio():
        if "user_id" not in session or session.get("role") != "worker":
            flash("Please log in as a worker.", "warning")
            return redirect(url_for("login"))

        bio = request.form.get("bio", "").strip()

        conn = get_db_connection()
        if conn is None:
            flash("Database connection failed.", "danger")
            return redirect(url_for("worker_dashboard"))

        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE worker_profiles SET bio = %s WHERE user_id = %s
            """, (bio or None, session["user_id"]))
            conn.commit()
            cursor.close()
            conn.close()
            flash("Bio updated successfully.", "success")
        except Exception as e:
            conn.rollback()
            cursor.close()
            conn.close()
            flash(f"Failed to update bio: {e}", "danger")

        return redirect(url_for("worker_dashboard"))

    # ---- Profile Details + Photo Update ----

    @app.route("/update_worker_profile", methods=["POST"])
    def update_worker_profile():
        """Handles phone number, hourly rate, and optional photo changes."""

        if "user_id" not in session or session.get("role") != "worker":
            flash("Please log in as a worker.", "warning")
            return redirect(url_for("login"))

        phone = request.form.get("phone", "").strip()
        hourly_rate_raw = request.form.get("hourly_rate", "").strip()

        # validate the hourly rate range
        try:
            hourly_rate = float(hourly_rate_raw)
            if hourly_rate < 50 or hourly_rate > 2000:
                flash("Hourly rate must be between ৳50 and ৳2000.", "warning")
                return redirect(url_for("worker_dashboard"))
        except (ValueError, TypeError):
            flash("Please enter a valid hourly rate.", "warning")
            return redirect(url_for("worker_dashboard"))

        # process photo if one was uploaded
        photo_url = None
        photo_file = request.files.get("photo")
        if photo_file and photo_file.filename:
            photo_url, photo_error = save_profile_photo(photo_file)
            if photo_error:
                flash(photo_error, "warning")
                return redirect(url_for("worker_dashboard"))

        conn = get_db_connection()
        if conn is None:
            flash("Database connection failed.", "danger")
            return redirect(url_for("worker_dashboard"))

        try:
            cursor = conn.cursor()

            # phone is stored in the users table
            cursor.execute("""
                UPDATE users SET phone = %s WHERE user_id = %s
            """, (phone or None, session["user_id"]))

            # rate and photo go in worker_profiles
            if photo_url:
                cursor.execute("""
                    UPDATE worker_profiles SET hourly_rate = %s, photo_url = %s WHERE user_id = %s
                """, (hourly_rate, photo_url, session["user_id"]))
            else:
                cursor.execute("""
                    UPDATE worker_profiles SET hourly_rate = %s WHERE user_id = %s
                """, (hourly_rate, session["user_id"]))

            conn.commit()
            cursor.close()
            conn.close()

            if photo_url:
                flash("Profile details and photo updated successfully.", "success")
            else:
                flash("Profile details updated successfully.", "success")
        except Exception as e:
            conn.rollback()
            cursor.close()
            conn.close()
            flash(f"Failed to update profile details: {e}", "danger")

        return redirect(url_for("worker_dashboard"))

    # ---- NID Verification (AJAX endpoint) ----

    @app.route("/verify_nid", methods=["POST"])
    def verify_nid():
        """Checks the NID against our dummy database and returns JSON.
        In production this would call a real government API."""

        nid_number = request.form.get("nid_number", "").strip()

        if not nid_number:
            return jsonify({"verified": False, "error": "Please enter an NID number."}), 400

        citizen = DUMMY_NID_DATABASE.get(nid_number)

        if citizen:
            # NID found - update the worker's verification status in the DB
            if "user_id" in session and session.get("role") == "worker":
                try:
                    conn = get_db_connection()
                    if conn:
                        cursor = conn.cursor()
                        cursor.execute("""
                            UPDATE worker_profiles
                            SET nid_number = %s, nid_verified = TRUE
                            WHERE user_id = %s
                        """, (nid_number, session["user_id"]))
                        conn.commit()
                        cursor.close()
                        conn.close()
                except Exception:
                    pass

            return jsonify({
                "verified": True,
                "citizen_name": citizen["name"],
                "dob": citizen["dob"],
                "address": citizen["address"],
            })
        else:
            return jsonify({
                "verified": False,
                "error": "NID not found in government database. Please double-check your number."
            })

    # ---- BRAC Training Toggle ----

    @app.route("/update_brac_training", methods=["POST"])
    def update_brac_training():
        if "user_id" not in session or session.get("role") != "worker":
            flash("Please log in as a worker.", "warning")
            return redirect(url_for("login"))

        brac_trained = request.form.get("brac_trained") == "1"

        conn = get_db_connection()
        if conn is None:
            flash("Database connection failed.", "danger")
            return redirect(url_for("worker_dashboard"))

        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE worker_profiles SET brac_trained = %s WHERE user_id = %s
            """, (brac_trained, session["user_id"]))
            conn.commit()
            cursor.close()
            conn.close()

            if brac_trained:
                flash("BRAC training status updated.", "success")
            else:
                flash("BRAC training status removed.", "info")
        except Exception as e:
            conn.rollback()
            if cursor is not None:
                cursor.close()
            conn.close()
            flash(f"Failed to update BRAC status: {e}", "danger")

        return redirect(url_for("worker_dashboard"))

    # ---- First-Time Profile Setup ----

    @app.route("/profile_setup", methods=["GET", "POST"])
    def profile_setup():
        """New workers land here after their first login.
        They fill in NID, hourly rate, skills, bio, and optional photo."""

        if "user_id" not in session or session.get("role") != "worker":
            flash("Please log in as a worker.", "warning")
            return redirect(url_for("login"))

        user_id = session["user_id"]

        if request.method == "POST":
            nid_number_raw      = request.form.get("nid_number", "").strip()
            hourly_rate         = request.form.get("hourly_rate", "0")
            availability_status = request.form.get("availability_status", "available")
            bio                 = request.form.get("bio", "").strip()
            selected_skills     = request.form.getlist("skills")
            nid_number          = nid_number_raw or None

            photo_url = None
            photo_file = request.files.get("photo")
            if photo_file and photo_file.filename:
                photo_url, photo_error = save_profile_photo(photo_file)
                if photo_error:
                    flash(photo_error, "warning")
                    return redirect(url_for("profile_setup"))

            conn = get_db_connection()
            if conn is None:
                flash("Database connection failed.", "danger")
                return redirect(url_for("profile_setup"))

            # check NID against our mock database
            nid_verified = bool(nid_number and nid_number in DUMMY_NID_DATABASE)

            try:
                cursor = conn.cursor()

                # create the worker profile row
                cursor.execute("""
                    INSERT INTO worker_profiles
                        (user_id, nid_number, nid_verified, hourly_rate, availability_status, photo_url, bio)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (user_id, nid_number, nid_verified, hourly_rate, availability_status, photo_url, bio or None))

                # link selected skills to this worker
                for skill_id in selected_skills:
                    cursor.execute("""
                        INSERT INTO worker_skills (worker_id, skill_id) VALUES (%s, %s)
                    """, (user_id, int(skill_id)))

                conn.commit()
                cursor.close()
                conn.close()

                if nid_verified:
                    flash("Profile created — NID verified successfully! ✓", "success")
                elif nid_number:
                    flash("Profile created, but NID could not be verified.", "warning")
                else:
                    flash("Profile created. You can verify your NID later from your dashboard.", "info")
                return redirect(url_for("worker_dashboard"))

            except Exception as e:
                conn.rollback()
                cursor.close()
                conn.close()
                flash(f"Profile setup failed: {e}", "danger")
                return redirect(url_for("profile_setup"))

        # GET request: show the setup form with skill options
        conn = get_db_connection()
        skills = []
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT skill_id, skill_name FROM skills ORDER BY skill_name")
            skills = cursor.fetchall()
            cursor.close()
            conn.close()

        return render_template("profile_setup.html", skills=skills)

    # ---- Skill Management ----

    @app.route("/add_skill", methods=["POST"])
    def add_skill():
        if "user_id" not in session or session.get("role") != "worker":
            flash("Please log in as a worker.", "warning")
            return redirect(url_for("login"))

        skill_id = request.form.get("skill_id")
        if not skill_id:
            flash("Please select a skill.", "warning")
            return redirect(url_for("worker_dashboard"))

        conn = get_db_connection()
        if conn is None:
            flash("Database connection failed.", "danger")
            return redirect(url_for("worker_dashboard"))

        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO worker_skills (worker_id, skill_id) VALUES (%s, %s)
            """, (session["user_id"], int(skill_id)))
            conn.commit()
            cursor.close()
            conn.close()
            flash("Skill added!", "success")
        except Exception as e:
            conn.rollback()
            cursor.close()
            conn.close()
            flash(f"Could not add skill: {e}", "danger")

        return redirect(url_for("worker_dashboard"))

    @app.route("/remove_skill", methods=["POST"])
    def remove_skill():
        if "user_id" not in session or session.get("role") != "worker":
            flash("Please log in as a worker.", "warning")
            return redirect(url_for("login"))

        skill_id = request.form.get("skill_id")
        if not skill_id:
            return redirect(url_for("worker_dashboard"))

        conn = get_db_connection()
        if conn is None:
            flash("Database connection failed.", "danger")
            return redirect(url_for("worker_dashboard"))

        try:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM worker_skills WHERE worker_id = %s AND skill_id = %s
            """, (session["user_id"], int(skill_id)))
            conn.commit()
            cursor.close()
            conn.close()
            flash("Skill removed.", "info")
        except Exception as e:
            conn.rollback()
            cursor.close()
            conn.close()
            flash(f"Could not remove skill: {e}", "danger")

        return redirect(url_for("worker_dashboard"))

    # ---- Public Worker Profile ----

    @app.route("/worker/profile/<int:worker_id>")
    def worker_profile(worker_id):
        """Anyone can view this page - shows the worker's details and reviews."""

        conn = get_db_connection()
        if conn is None:
            flash("Database connection failed. Please try again shortly.", "danger")
            return redirect(url_for("customer_dashboard"))

        try:
            cursor = conn.cursor(dictionary=True)
            verification_select, verification_group = get_background_verification_sql(cursor)

            # big query to get worker info with skills and rating averages
            cursor.execute(f"""
                SELECT u.user_id, u.full_name, u.phone, u.email,
                       wp.hourly_rate, wp.availability_status, wp.photo_url, wp.bio,
                       wp.nid_verified, {verification_select}, wp.brac_trained,
                       GROUP_CONCAT(DISTINCT s.skill_name SEPARATOR ', ') AS skills_list,
                       ROUND(AVG(r.stars), 1) AS avg_rating,
                       COUNT(DISTINCT r.rating_id) AS rating_count,
                       (SELECT COUNT(*) FROM ratings r2
                        WHERE r2.worker_id = u.user_id AND r2.review_text IS NOT NULL) AS review_count
                FROM users u
                INNER JOIN worker_profiles wp ON wp.user_id = u.user_id
                LEFT JOIN worker_skills ws ON ws.worker_id = u.user_id
                LEFT JOIN skills s ON s.skill_id = ws.skill_id
                LEFT JOIN ratings r ON r.worker_id = u.user_id
                WHERE u.user_id = %s AND u.role = 'worker'
                GROUP BY u.user_id, u.full_name, u.phone, u.email,
                         wp.hourly_rate, wp.availability_status, wp.photo_url, wp.bio,
                         wp.nid_verified{verification_group}, wp.brac_trained
            """, (worker_id,))
            worker = cursor.fetchone()

            if not worker:
                cursor.close()
                conn.close()
                flash("Worker not found.", "danger")
                return redirect(url_for("customer_dashboard"))

            # grab all text reviews for this worker, newest first
            cursor.execute("""
                SELECT r.stars, r.review_text, r.created_at,
                       u.full_name AS customer_name
                FROM ratings r
                LEFT JOIN bookings b ON b.booking_id = r.booking_id
                LEFT JOIN users u ON u.user_id = b.customer_id
                WHERE r.worker_id = %s AND r.review_text IS NOT NULL
                ORDER BY r.created_at DESC
            """, (worker_id,))
            reviews = cursor.fetchall()

            cursor.close()
            conn.close()

            return render_template("worker_profile.html", worker=worker, reviews=reviews)

        except Exception as e:
            print(f"[worker_profile] DB error: {e}")
            try:
                cursor.close()
                conn.close()
            except Exception:
                pass
            flash("Could not load worker profile right now.", "danger")
            return redirect(url_for("customer_dashboard"))
