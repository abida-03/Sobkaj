# admin.py - admin-only routes for the analytics dashboard and user management
# Only users with role='admin' can access these pages.

from flask import render_template, redirect, url_for, session, flash, request

from database.db_config import get_db_connection


def register_admin_routes(app):

    @app.route("/admin_dashboard")
    def admin_dashboard():
        # block non-admins
        if "user_id" not in session or session.get("role") != "admin":
            flash("Access denied. Admins only.", "danger")
            return redirect(url_for("login"))

        conn = get_db_connection()
        if conn is None:
            flash("Database connection failed.", "danger")
            return redirect(url_for("login"))

        cursor = conn.cursor(dictionary=True)

        # top 10 workers ranked by average rating
        cursor.execute("""
            SELECT
                u.user_id, u.full_name, u.phone,
                wp.hourly_rate, wp.availability_status,
                GROUP_CONCAT(DISTINCT s.skill_name ORDER BY s.skill_name SEPARATOR ', ') AS skills_list,
                ROUND(AVG(r.stars), 2)              AS avg_rating,
                COUNT(DISTINCT r.rating_id)         AS total_ratings,
                (SELECT COUNT(*) FROM ratings r2
                 WHERE r2.worker_id = u.user_id AND r2.review_text IS NOT NULL) AS total_reviews,
                COUNT(DISTINCT CASE WHEN b.status = 'completed' THEN b.booking_id END) AS completed_jobs
            FROM users u
            INNER JOIN worker_profiles wp ON wp.user_id   = u.user_id
            LEFT  JOIN ratings         r  ON r.worker_id  = u.user_id
            LEFT  JOIN bookings        b  ON b.worker_id  = u.user_id
            LEFT  JOIN worker_skills   ws ON ws.worker_id = u.user_id
            LEFT  JOIN skills          s  ON s.skill_id   = ws.skill_id
            WHERE u.role = 'worker'
            GROUP BY u.user_id, u.full_name, u.phone, wp.hourly_rate, wp.availability_status
            ORDER BY avg_rating DESC, completed_jobs DESC
            LIMIT 10
        """)
        top_workers = cursor.fetchall()

        # overall revenue from completed bookings
        cursor.execute("""
            SELECT
                COUNT(*)                                    AS total_completed_bookings,
                COALESCE(SUM(total_amount), 0.00)           AS total_revenue,
                COALESCE(ROUND(AVG(total_amount), 2), 0.00) AS avg_booking_value,
                COALESCE(MAX(total_amount), 0.00)           AS max_booking_value,
                COALESCE(MIN(total_amount), 0.00)           AS min_booking_value
            FROM bookings WHERE status = 'completed'
        """)
        revenue_stats = cursor.fetchone()

        # how much revenue and commission per booking status
        cursor.execute("""
            SELECT
                status,
                COUNT(*)                                   AS booking_count,
                COALESCE(SUM(total_amount), 0.00)          AS status_revenue,
                COALESCE(SUM(platform_commission), 0.00)   AS status_commission
            FROM bookings
            GROUP BY status
            ORDER BY FIELD(status, 'completed', 'confirmed', 'pending', 'cancelled')
        """)
        commission_by_status = cursor.fetchall()

        # total platform commission breakdown
        cursor.execute("""
            SELECT
                COALESCE(SUM(platform_commission), 0.00)   AS total_commission,
                COALESCE(SUM(CASE WHEN status = 'completed'
                             THEN platform_commission ELSE 0 END), 0.00) AS earned_commission,
                COALESCE(SUM(CASE WHEN status IN ('pending','confirmed')
                             THEN platform_commission ELSE 0 END), 0.00) AS pending_commission
            FROM bookings
        """)
        commission_totals = cursor.fetchone()

        # how many customers vs workers are registered
        cursor.execute("""
            SELECT
                COUNT(*)                                              AS total_users,
                SUM(CASE WHEN role = 'customer' THEN 1 ELSE 0 END)   AS total_customers,
                SUM(CASE WHEN role = 'worker'   THEN 1 ELSE 0 END)   AS total_workers
            FROM users WHERE role IN ('customer', 'worker')
        """)
        user_stats = cursor.fetchone()

        # full user list for the management table
        cursor.execute("""
            SELECT user_id, full_name, email, phone, role, created_at
            FROM users
            WHERE role IN ('customer', 'worker')
            ORDER BY role, full_name
        """)
        all_users = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template(
            "admin_dashboard.html",
            top_workers=top_workers,
            revenue_stats=revenue_stats,
            commission_by_status=commission_by_status,
            commission_totals=commission_totals,
            user_stats=user_stats,
            all_users=all_users,
        )

    @app.route("/admin/delete_user/<int:user_id>", methods=["POST"])
    def admin_delete_user(user_id):
        """Removes a customer or worker account. Admins can't delete other admins."""

        if "user_id" not in session or session.get("role") != "admin":
            flash("Access denied. Admins only.", "danger")
            return redirect(url_for("login"))

        conn = get_db_connection()
        if conn is None:
            flash("Database connection failed.", "danger")
            return redirect(url_for("admin_dashboard"))

        cursor = conn.cursor(dictionary=True)

        # check who we're about to delete
        cursor.execute("SELECT role, full_name FROM users WHERE user_id = %s", (user_id,))
        target = cursor.fetchone()

        if not target:
            flash("User not found.", "warning")
        elif target["role"] == "admin":
            flash("Cannot delete admin accounts.", "danger")
        else:
            # CASCADE will clean up their bookings, ratings, profile, etc.
            cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
            conn.commit()
            flash(f"{target['full_name']} ({target['role']}) has been removed.", "success")

        cursor.close()
        conn.close()
        return redirect(url_for("admin_dashboard"))
