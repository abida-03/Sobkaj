# customer.py - routes for the customer side of Sobkaj
# Profile editing, browsing workers, making bookings, viewing booking history, and leaving reviews.

from flask import render_template, request, redirect, url_for, session, flash

from config import PLATFORM_COMMISSION_RATE
from database.db_config import get_db_connection
from backend.helpers import get_background_verification_sql


def register_customer_routes(app):

    # ---- Customer Profile ----

    @app.route("/customer/profile", methods=["GET", "POST"])
    def customer_profile():
        if "user_id" not in session or session.get("role") != "customer":
            flash("Please log in as a customer.", "warning")
            return redirect(url_for("login"))

        conn = get_db_connection()
        if conn is None:
            flash("Database connection failed.", "danger")
            return redirect(url_for("customer_dashboard"))

        if request.method == "POST":
            full_name = request.form.get("full_name", "").strip()
            phone = request.form.get("phone", "").strip()

            try:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE users SET full_name = %s, phone = %s WHERE user_id = %s
                """, (full_name, phone or None, session["user_id"]))
                conn.commit()
                session["full_name"] = full_name
                flash("Profile updated successfully.", "success")
            except Exception as e:
                conn.rollback()
                flash(f"Failed to update profile: {e}", "danger")
            finally:
                cursor.close()

        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT full_name, email, phone FROM users WHERE user_id = %s", (session["user_id"],))
            customer = cursor.fetchone()
            cursor.close()
        except Exception as e:
            customer = {}
            flash(f"Failed to load profile: {e}", "danger")
        finally:
            conn.close()

        return render_template("customer_profile.html", customer=customer)

    # ---- Customer Dashboard (Browse Workers) ----

    @app.route("/customer/dashboard")
    def customer_dashboard():
        """Main page for customers - shows all workers with optional search filters."""

        search_skill = request.args.get("skill", "").strip()
        search_name  = request.args.get("name", "").strip()

        conn = get_db_connection()
        if conn is None:
            flash("Database connection failed. Please try again shortly.", "danger")
            return render_template("customer_dashboard.html",
                                   workers=[], all_skills=[],
                                   search_skill="", search_name="")

        try:
            cursor = conn.cursor(dictionary=True)

            # grab the full skill list for the dropdown filter
            cursor.execute("SELECT skill_id, skill_name FROM skills ORDER BY skill_name")
            all_skills = cursor.fetchall()

            # handle the column name difference across DB versions
            verification_select, verification_group = get_background_verification_sql(cursor)

            # big query: join workers with their profiles, skills, and ratings
            # GROUP_CONCAT merges multiple skills into a comma-separated string
            base_query = f"""
                SELECT
                    u.user_id, u.full_name, u.phone,
                    wp.hourly_rate, wp.availability_status, wp.photo_url, wp.bio,
                    wp.nid_verified, {verification_select}, wp.brac_trained,
                    GROUP_CONCAT(DISTINCT s.skill_name SEPARATOR ', ') AS skills_list,
                    ROUND(AVG(r.stars), 1) AS avg_rating,
                    COUNT(DISTINCT r.rating_id) AS rating_count,
                    (SELECT COUNT(*) FROM ratings r2
                     WHERE r2.worker_id = u.user_id AND r2.review_text IS NOT NULL) AS review_count
                FROM users u
                INNER JOIN worker_profiles wp ON wp.user_id = u.user_id
                INNER JOIN worker_skills  ws ON ws.worker_id = u.user_id
                INNER JOIN skills         s  ON s.skill_id   = ws.skill_id
                LEFT  JOIN ratings        r  ON r.worker_id  = u.user_id
                WHERE u.role = 'worker'
            """
            params = []

            # add skill filter if the user selected one
            if search_skill:
                base_query += """
                    AND u.user_id IN (
                        SELECT ws2.worker_id FROM worker_skills ws2
                        INNER JOIN skills s2 ON s2.skill_id = ws2.skill_id
                        WHERE s2.skill_name = %s
                    )
                """
                params.append(search_skill)

            # add name search if the user typed something
            if search_name:
                base_query += " AND u.full_name LIKE %s"
                params.append(f"%{search_name}%")

            # group by all non-aggregated columns, sort best-rated first
            base_query += f"""
                GROUP BY u.user_id, u.full_name, u.phone,
                         wp.hourly_rate, wp.availability_status,
                         wp.photo_url, wp.bio, wp.nid_verified{verification_group}, wp.brac_trained
                ORDER BY avg_rating DESC, wp.hourly_rate ASC
            """

            cursor.execute(base_query, tuple(params))
            workers = cursor.fetchall()
            cursor.close()
            conn.close()

            return render_template("customer_dashboard.html",
                                   workers=workers,
                                   all_skills=all_skills,
                                   search_skill=search_skill,
                                   search_name=search_name)
        except Exception as e:
            print(f"[customer_dashboard] DB error: {e}")
            try:
                cursor.close()
                conn.close()
            except Exception:
                pass
            flash("Could not load workers right now. Please try again shortly.", "danger")
            return render_template("customer_dashboard.html",
                                   workers=[], all_skills=[],
                                   search_skill="", search_name="")

    # ---- Booking a Worker ----

    @app.route("/book/<int:worker_id>", methods=["POST"])
    def book_worker(worker_id):
        """Creates a new booking. Uses a transaction so if something fails midway,
        nothing gets saved (atomicity)."""

        if "user_id" not in session:
            flash("Please log in or register to book a worker.", "warning")
            return redirect(url_for("login"))

        if session.get("role") == "worker":
            flash("Worker accounts cannot book other workers. Please use a customer account.", "warning")
            return redirect(url_for("customer_dashboard"))

        if session.get("role") != "customer":
            flash("Only customers can make bookings.", "warning")
            return redirect(url_for("login"))

        service_date    = request.form.get("service_date", "")
        service_time    = request.form.get("service_time", "09:00:00")
        hours_requested = request.form.get("hours_requested", "1")

        if not service_date or not service_time:
            flash("Please select a service date and time.", "danger")
            return redirect(url_for("customer_dashboard"))

        conn = get_db_connection()
        if conn is None:
            flash("Database connection failed.", "danger")
            return redirect(url_for("customer_dashboard"))

        try:
            conn.start_transaction()
            cursor = conn.cursor(dictionary=True)

            # fetch rate to calculate total
            cursor.execute("""
                SELECT hourly_rate FROM worker_profiles WHERE user_id = %s
            """, (worker_id,))
            worker = cursor.fetchone()

            if not worker:
                conn.rollback()
                cursor.close()
                conn.close()
                flash("Worker profile not found.", "danger")
                return redirect(url_for("customer_dashboard"))

            # price calculation: total = rate * hours, commission = 5% of total
            hours  = float(hours_requested)
            rate   = float(worker["hourly_rate"])
            total_amount        = round(rate * hours, 2)
            platform_commission = round(total_amount * PLATFORM_COMMISSION_RATE, 2)

            cursor.execute("""
                INSERT INTO bookings
                    (customer_id, worker_id, service_date, service_time, hours_requested,
                     total_amount, platform_commission, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'pending')
            """, (
                session["user_id"], worker_id, service_date, service_time,
                hours, total_amount, platform_commission
            ))

            conn.commit()
            cursor.close()
            conn.close()
            flash("Booking confirmed!", "success")

        except Exception as e:
            conn.rollback()
            cursor.close()
            conn.close()
            flash(f"Booking failed (rolled back): {e}", "danger")

        return redirect(url_for("customer_dashboard"))

    # ---- Booking History ----

    @app.route("/my_bookings")
    def my_bookings():
        if "user_id" not in session or session.get("role") != "customer":
            flash("Please log in as a customer.", "warning")
            return redirect(url_for("login"))

        conn = get_db_connection()
        if conn is None:
            flash("Database connection failed.", "danger")
            return redirect(url_for("login"))

        cursor = conn.cursor(dictionary=True)
        # fetch all bookings with the worker's name, plus whether a review exists
        cursor.execute("""
            SELECT b.*, u.full_name AS worker_name,
                   (SELECT COUNT(*) FROM ratings r WHERE r.booking_id = b.booking_id) AS has_review
            FROM bookings b
            INNER JOIN users u ON u.user_id = b.worker_id
            WHERE b.customer_id = %s
            ORDER BY b.service_date DESC, b.service_time ASC
        """, (session["user_id"],))
        bookings = cursor.fetchall()
        cursor.close()
        conn.close()

        return render_template("my_bookings.html", bookings=bookings)

    # ---- Leaving a Review ----

    @app.route("/leave_review/<int:booking_id>", methods=["GET", "POST"])
    def leave_review(booking_id):
        if "user_id" not in session or session.get("role") != "customer":
            flash("Please log in as a customer.", "warning")
            return redirect(url_for("login"))

        conn = get_db_connection()
        if conn is None:
            flash("Database connection failed.", "danger")
            return redirect(url_for("my_bookings"))

        cursor = conn.cursor(dictionary=True)

        # make sure this booking belongs to the logged-in customer
        cursor.execute("""
            SELECT b.*, u.full_name AS worker_name
            FROM bookings b
            INNER JOIN users u ON u.user_id = b.worker_id
            WHERE b.booking_id = %s AND b.customer_id = %s
        """, (booking_id, session["user_id"]))
        booking = cursor.fetchone()

        if not booking:
            cursor.close()
            conn.close()
            flash("Booking not found.", "danger")
            return redirect(url_for("my_bookings"))

        # reviews only allowed for completed work
        if booking["status"] != "completed":
            cursor.close()
            conn.close()
            flash("You can only review completed bookings.", "warning")
            return redirect(url_for("my_bookings"))

        # one review per booking
        cursor.execute("SELECT rating_id FROM ratings WHERE booking_id = %s", (booking_id,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            flash("You have already reviewed this booking.", "info")
            return redirect(url_for("my_bookings"))

        if request.method == "POST":
            stars       = request.form.get("stars", "5")
            review_text = request.form.get("review_text", "").strip()

            try:
                cursor.execute("""
                    INSERT INTO ratings (booking_id, customer_id, worker_id, stars, review_text)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    booking_id,
                    session["user_id"],
                    booking["worker_id"],
                    int(stars),
                    review_text or None
                ))
                conn.commit()
                cursor.close()
                conn.close()
                flash("Thank you for your review!", "success")
                return redirect(url_for("my_bookings"))
            except Exception as e:
                conn.rollback()
                cursor.close()
                conn.close()
                flash(f"Failed to submit review: {e}", "danger")
                return redirect(url_for("my_bookings"))

        cursor.close()
        conn.close()
        return render_template("leave_review.html", booking=booking)
