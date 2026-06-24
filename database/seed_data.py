# seed_data.py - fills the database with realistic dummy data for demo and testing
# Run this with: python seed_data.py
# All generated users use the password: Test@123

from __future__ import annotations

import random
from datetime import date, timedelta
from typing import Dict, List, Set, Tuple

from werkzeug.security import generate_password_hash

from config import PLATFORM_COMMISSION_RATE
from database.db_config import get_db_connection

# shared password hash so we don't re-hash for every user
PASSWORD_HASH = generate_password_hash("Test@123")

# fixed seed for reproducible results (same data every time we run it)
RNG = random.Random(2604)

# the 8 service categories our platform offers
SKILLS = [
    ("Plumber", "Fixes pipes, faucets, and drainage systems"),
    ("Electrician", "Handles wiring, electrical repairs, and installations"),
    ("Maid", "Provides cleaning and household maintenance services"),
    ("Babysitter", "Takes care of children in the absence of parents"),
    ("Carpenter", "Builds and repairs wooden structures and furniture"),
    ("Painter", "Paints walls, ceilings, and exterior surfaces"),
    ("Tutor", "Provides academic tutoring and homework help"),
    ("Cook", "Prepares meals and manages kitchen duties"),
]

# 24 dummy customers with Bangladeshi names and local phone numbers
CUSTOMERS = [
    ("Rafiq Ahmed", "rafiq.ahmed@gmail.com", "01711234567"),
    ("Fatima Begum", "fatima.begum@yahoo.com", "01812345678"),
    ("Kamal Hossain", "kamal.hossain@outlook.com", "01912456789"),
    ("Nusrat Jahan", "nusrat.jahan@gmail.com", "01611234567"),
    ("Shahidul Islam", "shahidul.islam@gmail.com", "01511987654"),
    ("Taslima Akter", "taslima.akter@hotmail.com", "01711456789"),
    ("Imran Khan", "imran.khan@gmail.com", "01811234890"),
    ("Sharmin Sultana", "sharmin.sultana@yahoo.com", "01911234567"),
    ("Anisur Rahman", "anisur.rahman@gmail.com", "01612345890"),
    ("Rubina Khatun", "rubina.khatun@outlook.com", "01512345678"),
    ("Jamal Uddin", "jamal.uddin@gmail.com", "01711567890"),
    ("Nasreen Pervin", "nasreen.pervin@gmail.com", "01812567890"),
    ("Harun Rashid", "harun.rashid@yahoo.com", "01912567890"),
    ("Salma Khanam", "salma.khanam@gmail.com", "01611567890"),
    ("Belal Hossain", "belal.hossain@outlook.com", "01511567890"),
    ("Farida Yasmin", "farida.yasmin@gmail.com", "01711678901"),
    ("Mizanur Rahman", "mizanur.rahman@yahoo.com", "01812678901"),
    ("Sumaiya Islam", "sumaiya.islam@gmail.com", "01912678901"),
    ("Rakibul Hasan", "rakibul.hasan@outlook.com", "01612678901"),
    ("Nurjahan Begum", "nurjahan.begum@gmail.com", "01512678901"),
    ("Mehedi Hasan", "mehedi.hasan@gmail.com", "01711789012"),
    ("Sadia Rahman", "sadia.rahman@yahoo.com", "01812789012"),
    ("Arif Chowdhury", "arif.chowdhury@gmail.com", "01912789012"),
    ("Laboni Akter", "laboni.akter@outlook.com", "01612789012"),
]

# 24 dummy workers with different skill sets and rates
WORKERS = [
    {
        "name": "Abul Kalam",
        "email": "abul.kalam.worker@gmail.com",
        "phone": "01721000001",
        "skills": ["Plumber", "Carpenter"],
        "hourly_rate": 380,
        "status": "available",
        "bio": "I handle urgent plumbing and pipe repairs, with practical solutions that fit apartments and family homes.",
    },
    {
        "name": "Shamsul Haque",
        "email": "shamsul.haque.worker@gmail.com",
        "phone": "01721000002",
        "skills": ["Electrician"],
        "hourly_rate": 420,
        "status": "busy",
        "bio": "I do electrical rewiring, switchboard fixes, and safety checks for homes and shops.",
    },
    {
        "name": "Monira Khatun",
        "email": "monira.khatun.worker@gmail.com",
        "phone": "01721000003",
        "skills": ["Maid", "Cook"],
        "hourly_rate": 240,
        "status": "available",
        "bio": "I provide deep cleaning and home-style cooking with attention to hygiene and schedule.",
    },
    {
        "name": "Rahim Mia",
        "email": "rahim.mia.worker@gmail.com",
        "phone": "01721000004",
        "skills": ["Carpenter"],
        "hourly_rate": 360,
        "status": "offline",
        "bio": "I repair doors, cabinets, and wooden furniture with durable finishing.",
    },
    {
        "name": "Kulsum Begum",
        "email": "kulsum.begum.worker@gmail.com",
        "phone": "01721000005",
        "skills": ["Babysitter", "Tutor"],
        "hourly_rate": 260,
        "status": "available",
        "bio": "I support child care routines and homework sessions for primary school learners.",
    },
    {
        "name": "Mokhlesur Rahman",
        "email": "mokhlesur.rahman.worker@gmail.com",
        "phone": "01721000006",
        "skills": ["Painter"],
        "hourly_rate": 320,
        "status": "available",
        "bio": "I do wall preparation and interior painting with clean edge finishing.",
    },
    {
        "name": "Hasina Akter",
        "email": "hasina.akter.worker@gmail.com",
        "phone": "01721000007",
        "skills": ["Maid"],
        "hourly_rate": 210,
        "status": "busy",
        "bio": "I offer regular household cleaning and kitchen support for working families.",
    },
    {
        "name": "Nazrul Islam",
        "email": "nazrul.islam.worker@gmail.com",
        "phone": "01721000008",
        "skills": ["Electrician", "Plumber"],
        "hourly_rate": 450,
        "status": "available",
        "bio": "I handle mixed utility jobs including wiring faults and water line leaks.",
    },
    {
        "name": "Roksana Parvin",
        "email": "roksana.parvin.worker@gmail.com",
        "phone": "01721000009",
        "skills": ["Tutor"],
        "hourly_rate": 280,
        "status": "available",
        "bio": "I teach English and math with weekly progress tracking for students.",
    },
    {
        "name": "Abdul Mannan",
        "email": "abdul.mannan.worker@gmail.com",
        "phone": "01721000010",
        "skills": ["Cook"],
        "hourly_rate": 300,
        "status": "available",
        "bio": "I prepare Bengali meals for daily service and small family gatherings.",
    },
    {
        "name": "Shamima Nasreen",
        "email": "shamima.nasreen.worker@gmail.com",
        "phone": "01721000011",
        "skills": ["Babysitter"],
        "hourly_rate": 250,
        "status": "offline",
        "bio": "I provide patient child supervision and meal assistance during evening shifts.",
    },
    {
        "name": "Dulal Mia",
        "email": "dulal.mia.worker@gmail.com",
        "phone": "01721000012",
        "skills": ["Plumber"],
        "hourly_rate": 340,
        "status": "available",
        "bio": "I fix blocked drains and bathroom fittings with transparent pricing.",
    },
    {
        "name": "Karim Sheikh",
        "email": "karim.sheikh.worker@gmail.com",
        "phone": "01721000013",
        "skills": ["Electrician"],
        "hourly_rate": 470,
        "status": "available",
        "bio": "I focus on AC wiring, inverter setup, and fault diagnosis for apartments.",
    },
    {
        "name": "Rashida Begum",
        "email": "rashida.begum.worker@gmail.com",
        "phone": "01721000014",
        "skills": ["Maid", "Babysitter"],
        "hourly_rate": 230,
        "status": "busy",
        "bio": "I support families with cleaning, child care, and elder-friendly routines.",
    },
    {
        "name": "Jakir Hossain",
        "email": "jakir.hossain.worker@gmail.com",
        "phone": "01721000015",
        "skills": ["Electrician", "Carpenter"],
        "hourly_rate": 510,
        "status": "available",
        "bio": "I repair appliances and wooden fixtures, ideal for full home maintenance visits.",
    },
    {
        "name": "Amena Khatun",
        "email": "amena.khatun.worker@gmail.com",
        "phone": "01721000016",
        "skills": ["Cook", "Maid"],
        "hourly_rate": 220,
        "status": "available",
        "bio": "I provide practical meal prep and routine cleaning support for busy homes.",
    },
    {
        "name": "Sobuj Ahmed",
        "email": "sobuj.ahmed.worker@gmail.com",
        "phone": "01721000017",
        "skills": ["Painter", "Carpenter"],
        "hourly_rate": 390,
        "status": "available",
        "bio": "I handle paint touch-ups, furniture repair, and room refresh projects.",
    },
    {
        "name": "Ruma Akter",
        "email": "ruma.akter.worker@gmail.com",
        "phone": "01721000018",
        "skills": ["Tutor", "Babysitter"],
        "hourly_rate": 270,
        "status": "available",
        "bio": "I assist school-age children with homework and structured study sessions.",
    },
    {
        "name": "Babul Mia",
        "email": "babul.mia.worker@gmail.com",
        "phone": "01721000019",
        "skills": ["Plumber", "Painter"],
        "hourly_rate": 330,
        "status": "busy",
        "bio": "I combine plumbing and paint jobs for renovation-ready service calls.",
    },
    {
        "name": "Jharna Begum",
        "email": "jharna.begum.worker@gmail.com",
        "phone": "01721000020",
        "skills": ["Maid"],
        "hourly_rate": 200,
        "status": "available",
        "bio": "I focus on kitchen cleaning, laundry support, and regular upkeep.",
    },
    {
        "name": "Selim Reza",
        "email": "selim.reza.worker@gmail.com",
        "phone": "01721000021",
        "skills": ["Electrician"],
        "hourly_rate": 430,
        "status": "available",
        "bio": "I do socket upgrades, breaker fixes, and short-circuit troubleshooting.",
    },
    {
        "name": "Parul Sultana",
        "email": "parul.sultana.worker@gmail.com",
        "phone": "01721000022",
        "skills": ["Cook"],
        "hourly_rate": 260,
        "status": "offline",
        "bio": "I prepare home-style meals and support event meal prep when needed.",
    },
    {
        "name": "Masud Rana",
        "email": "masud.rana.worker@gmail.com",
        "phone": "01721000023",
        "skills": ["Carpenter"],
        "hourly_rate": 410,
        "status": "available",
        "bio": "I build storage shelves and repair doors, windows, and bed frames.",
    },
    {
        "name": "Shila Akter",
        "email": "shila.akter.worker@gmail.com",
        "phone": "01721000024",
        "skills": ["Tutor", "Maid"],
        "hourly_rate": 240,
        "status": "available",
        "bio": "I help with child studies and keep study spaces tidy and organized.",
    },
]

# sample review texts used when generating fake ratings
BAD_REVIEW_TEXTS = [
    "Very poor job quality. I had to call another worker to fix the issue.",
    "Arrived late and left work incomplete. Not satisfied with the service.",
    "Rude communication and careless work. Would not book again.",
    "The service was below expectation and too expensive for the result.",
    "Missed key requirements and did not follow instructions properly.",
    "Messy work, poor finishing, and delayed completion.",
]

GOOD_REVIEW_TEXTS = [
    "Work quality was good and communication was smooth.",
    "Professional behavior and completed the task properly.",
    "Satisfied with the service. Will consider booking again.",
    "On-time service with decent quality and clear updates.",
    "Helpful worker and cooperative throughout the booking.",
]


def get_avatar_url(name: str) -> str:
    """Generates a placeholder avatar using ui-avatars.com API."""
    colors = ["264653", "2a9d8f", "e76f51", "f4a261", "1d3557", "457b9d"]
    background = RNG.choice(colors)
    encoded_name = name.replace(" ", "+")
    return f"https://ui-avatars.com/api/?name={encoded_name}&background={background}&color=fff&size=220"


def generate_nid(index: int) -> str:
    """Creates a fake NID number for demo purposes."""
    return f"{1990 + (index % 10)}{RNG.randint(100000000, 999999999)}"


def pick_stars(worker_index: int) -> int:
    """Assigns star ratings with a weighted distribution.
    First batch of workers get lower ratings to create variety in the data."""
    if worker_index < 14:
        return RNG.choice([1, 1, 2, 2, 2, 3])
    if worker_index < 20:
        return RNG.choice([1, 2, 3, 3, 4])
    return RNG.choice([3, 4, 4, 5, 5])


def ensure_skills(cursor) -> Dict[str, int]:
    """Makes sure all skill categories exist, returns a name->id mapping."""
    for name, description in SKILLS:
        cursor.execute(
            "INSERT IGNORE INTO skills (skill_name, description) VALUES (%s, %s)",
            (name, description),
        )

    cursor.execute("SELECT skill_id, skill_name FROM skills")
    return {skill_name: skill_id for skill_id, skill_name in cursor.fetchall()}


def clear_existing_data(cursor) -> None:
    """Wipes all transactional data so we start fresh.
    Disables FK checks temporarily to avoid constraint errors during bulk delete."""
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    cursor.execute("DELETE FROM ratings")
    cursor.execute("DELETE FROM bookings")
    cursor.execute("DELETE FROM worker_skills")
    cursor.execute("DELETE FROM worker_profiles")
    cursor.execute("DELETE FROM users")
    cursor.execute("ALTER TABLE users AUTO_INCREMENT = 1")
    cursor.execute("ALTER TABLE worker_profiles AUTO_INCREMENT = 1")
    cursor.execute("ALTER TABLE bookings AUTO_INCREMENT = 1")
    cursor.execute("ALTER TABLE ratings AUTO_INCREMENT = 1")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")


def insert_users(cursor, users: List[Tuple[str, str, str]], role: str) -> None:
    """Bulk-inserts a list of users with the given role."""
    for full_name, email, phone in users:
        cursor.execute(
            """
            INSERT INTO users (full_name, email, password_hash, role, phone)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (full_name, email, PASSWORD_HASH, role, phone),
        )


def create_profiles(
    cursor,
    worker_rows: List[Tuple[int, str]],
    skill_map: Dict[str, int],
) -> Tuple[Dict[int, float], Set[int]]:
    """Creates worker_profiles and assigns skills.
    Splits workers into tiers: BRAC-trained, verified-only, and unverified.
    Returns hourly rates and the set of unverified worker IDs."""

    total_workers = len(worker_rows)
    none_count = max(1, int(round(total_workers * 0.05)))
    none_count = min(none_count, total_workers)

    verified_count = total_workers - none_count
    brac_verified_count = int(round(verified_count * 0.60))
    brac_verified_count = max(0, min(brac_verified_count, verified_count))
    verified_only_count = verified_count - brac_verified_count

    hourly_rates: Dict[int, float] = {}
    none_worker_ids: Set[int] = set()

    for idx, (worker_id, worker_name) in enumerate(worker_rows):
        worker_meta = WORKERS[idx]

        # split into quality tiers
        if idx < brac_verified_count:
            background_verified = 1
            brac_trained = 1
        elif idx < brac_verified_count + verified_only_count:
            background_verified = 1
            brac_trained = 0
        else:
            background_verified = 0
            brac_trained = 0
            none_worker_ids.add(worker_id)

        nid_number = generate_nid(idx)
        photo_url = get_avatar_url(worker_name)

        hourly_rate = float(worker_meta["hourly_rate"])
        availability_status = worker_meta["status"]

        # unverified workers get lower rates and show as offline
        if worker_id in none_worker_ids:
            hourly_rate = min(hourly_rate, 180.0)
            availability_status = "offline"

        cursor.execute(
            """
            INSERT INTO worker_profiles (
                user_id, nid_number, nid_verified, background_verified,
                brac_trained, hourly_rate, availability_status, photo_url, bio
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                worker_id,
                nid_number,
                background_verified,
                background_verified,
                brac_trained,
                hourly_rate,
                availability_status,
                photo_url,
                worker_meta["bio"],
            ),
        )

        hourly_rates[worker_id] = hourly_rate

        # assign skills from the worker's skill list
        for skill_name in worker_meta["skills"]:
            cursor.execute(
                "INSERT INTO worker_skills (worker_id, skill_id) VALUES (%s, %s)",
                (worker_id, skill_map[skill_name]),
            )

    return hourly_rates, none_worker_ids


def create_rating_bookings(
    cursor,
    customer_ids: List[int],
    worker_rows: List[Tuple[int, str]],
    hourly_rates: Dict[int, float],
    none_worker_ids: Set[int],
) -> None:
    """Generates completed bookings with ratings, plus some future bookings.
    This gives us enough data to test the dashboard, reviews, and admin analytics."""

    today = date.today()
    worker_ids = [wid for wid, _ in worker_rows]
    regular_worker_ids = [wid for wid in worker_ids if wid not in none_worker_ids]

    # most workers should have more ratings than text reviews (realistic)
    workers_with_more_ratings_than_reviews = set(regular_worker_ids)
    if len(regular_worker_ids) > 4:
        for worker_id in RNG.sample(regular_worker_ids, k=2):
            workers_with_more_ratings_than_reviews.discard(worker_id)

    for worker_index, worker_id in enumerate(worker_ids):
        # unverified workers get fewer bookings
        if worker_id in none_worker_ids:
            total_ratings = RNG.randint(1, 3)
            reviews_for_worker = RNG.randint(0, min(1, total_ratings))
        else:
            total_ratings = RNG.randint(7, 12)
            if worker_id in workers_with_more_ratings_than_reviews:
                reviews_for_worker = max(1, total_ratings - RNG.randint(2, 5))
            else:
                reviews_for_worker = max(1, total_ratings - RNG.randint(0, 1))

        for rating_index in range(total_ratings):
            customer_id = RNG.choice(customer_ids)
            days_ago = RNG.randint(3, 140)
            service_date = today - timedelta(days=days_ago)
            hours = RNG.choice([2.0, 2.5, 3.0, 4.0, 5.0, 6.0])
            total_amount = round(hourly_rates[worker_id] * hours, 2)
            commission = round(total_amount * PLATFORM_COMMISSION_RATE, 2)

            cursor.execute(
                """
                INSERT INTO bookings (
                    customer_id, worker_id, service_date, hours_requested,
                    total_amount, platform_commission, status
                ) VALUES (%s, %s, %s, %s, %s, %s, 'completed')
                """,
                (customer_id, worker_id, service_date, hours, total_amount, commission),
            )
            booking_id = cursor.lastrowid

            if worker_id in none_worker_ids:
                stars = RNG.choice([1, 2, 2, 3])
            else:
                stars = pick_stars(worker_index)
            review_text = None

            # only some ratings include written reviews
            if rating_index < reviews_for_worker:
                if stars <= 2:
                    review_text = RNG.choice(BAD_REVIEW_TEXTS)
                else:
                    review_text = RNG.choice(GOOD_REVIEW_TEXTS)

            cursor.execute(
                """
                INSERT INTO ratings (booking_id, customer_id, worker_id, stars, review_text)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (booking_id, customer_id, worker_id, stars, review_text),
            )

    # create 20 future bookings with mixed statuses for testing
    future_worker_pool = regular_worker_ids or worker_ids

    for _ in range(20):
        customer_id = RNG.choice(customer_ids)
        worker_id = RNG.choice(future_worker_pool)
        days_ahead = RNG.randint(1, 20)
        service_date = today + timedelta(days=days_ahead)
        hours = RNG.choice([2.0, 3.0, 4.0, 5.0])
        total_amount = round(hourly_rates[worker_id] * hours, 2)
        commission = round(total_amount * PLATFORM_COMMISSION_RATE, 2)
        status = RNG.choice(["pending", "confirmed", "cancelled"])

        cursor.execute(
            """
            INSERT INTO bookings (
                customer_id, worker_id, service_date, hours_requested,
                total_amount, platform_commission, status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (customer_id, worker_id, service_date, hours, total_amount, commission, status),
        )


def print_summary(cursor) -> None:
    """Prints a report of what was seeded so we can verify the data looks right."""

    cursor.execute(
        """
        SELECT
            COUNT(*) AS worker_total,
            SUM(CASE WHEN brac_trained = 1 THEN 1 ELSE 0 END) AS brac_total,
            SUM(CASE WHEN background_verified = 1 THEN 1 ELSE 0 END) AS verified_total,
            SUM(CASE WHEN background_verified = 1 AND brac_trained = 0 THEN 1 ELSE 0 END) AS verified_only_total,
            SUM(CASE WHEN background_verified = 0 AND brac_trained = 0 THEN 1 ELSE 0 END) AS none_total
        FROM worker_profiles
        """
    )
    worker_stats = cursor.fetchone()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM worker_profiles
        WHERE brac_trained = 1 AND background_verified = 0
        """
    )
    invalid_brac_verified = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT
            COUNT(*) AS workers_with_ratings,
            SUM(CASE WHEN rating_count > review_count THEN 1 ELSE 0 END) AS workers_more_ratings
        FROM (
            SELECT
                worker_id,
                COUNT(*) AS rating_count,
                SUM(CASE WHEN review_text IS NOT NULL AND TRIM(review_text) <> '' THEN 1 ELSE 0 END) AS review_count
            FROM ratings
            GROUP BY worker_id
        ) grouped
        """
    )
    rating_distribution = cursor.fetchone()

    cursor.execute("SELECT COUNT(*) FROM ratings")
    total_ratings = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM ratings WHERE review_text IS NOT NULL AND TRIM(review_text) <> ''"
    )
    total_reviews = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM ratings WHERE stars <= 2")
    bad_ratings = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM ratings
        WHERE stars <= 2 AND review_text IS NOT NULL AND TRIM(review_text) <> ''
        """
    )
    bad_reviews = cursor.fetchone()[0]

    workers_with_ratings = rating_distribution[0] or 0
    workers_more_ratings = rating_distribution[1] or 0
    majority_threshold = workers_with_ratings / 2
    verified_rate = ((worker_stats[2] or 0) / worker_stats[0] * 100) if worker_stats[0] else 0.0
    brac_within_verified_rate = ((worker_stats[1] or 0) / worker_stats[2] * 100) if worker_stats[2] else 0.0
    none_rate = ((worker_stats[4] or 0) / worker_stats[0] * 100) if worker_stats[0] else 0.0

    print("\n" + "=" * 68)
    print("SEED COMPLETE")
    print("=" * 68)
    print(f"Workers total: {worker_stats[0]}")
    print(f"BRAC trained: {worker_stats[1]}")
    print(f"Verified total: {worker_stats[2]}")
    print(f"Verified rate: {verified_rate:.1f}%")
    print(f"Verified but not BRAC trained: {worker_stats[3]}")
    print(f"Neither verified nor BRAC trained: {worker_stats[4]}")
    print(f"None group rate: {none_rate:.1f}%")
    print(f"BRAC within verified: {brac_within_verified_rate:.1f}%")
    print(f"Invalid BRAC without verification (must be 0): {invalid_brac_verified}")
    print("-" * 68)
    print(f"Total ratings: {total_ratings}")
    print(f"Total reviews (text present): {total_reviews}")
    print(f"Bad ratings (1-2 stars): {bad_ratings}")
    print(f"Bad ratings with review text: {bad_reviews}")
    print("-" * 68)
    print(f"Workers with ratings: {workers_with_ratings}")
    print(f"Workers where ratings > reviews: {workers_more_ratings}")
    print(f"Majority satisfied: {workers_more_ratings > majority_threshold}")
    print("=" * 68)
    print("Login password for all dummy users: Test@123")


def seed_database() -> bool:
    """Main seeding function. Runs all steps inside a single transaction."""

    conn = get_db_connection()
    if not conn:
        print("[ERROR] Database connection failed. Start MySQL and retry.")
        return False

    cursor = conn.cursor()

    try:
        print("[1/6] Clearing existing transactional data...")
        clear_existing_data(cursor)

        print("[2/6] Ensuring skill catalog...")
        skill_map = ensure_skills(cursor)

        print(f"[3/6] Creating {len(CUSTOMERS)} customers...")
        insert_users(cursor, CUSTOMERS, "customer")

        print(f"[4/6] Creating {len(WORKERS)} workers...")
        worker_user_rows = [(w["name"], w["email"], w["phone"]) for w in WORKERS]
        insert_users(cursor, worker_user_rows, "worker")

        cursor.execute(
            "SELECT user_id, full_name FROM users WHERE role = 'worker' ORDER BY user_id"
        )
        worker_rows = cursor.fetchall()

        cursor.execute("SELECT user_id FROM users WHERE role = 'customer' ORDER BY user_id")
        customer_ids = [row[0] for row in cursor.fetchall()]

        print("[5/6] Building worker profiles and skills...")
        hourly_rates, none_worker_ids = create_profiles(cursor, worker_rows, skill_map)

        print("[6/6] Creating bookings, ratings, and reviews...")
        create_rating_bookings(cursor, customer_ids, worker_rows, hourly_rates, none_worker_ids)

        conn.commit()
        print_summary(cursor)

        cursor.close()
        conn.close()
        return True

    except Exception as exc:
        conn.rollback()
        cursor.close()
        conn.close()
        print(f"[ERROR] Seeding failed: {exc}")
        return False


if __name__ == "__main__":
    seed_database()
