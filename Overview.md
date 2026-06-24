# Sobkaj Project Overview

## 1. Project Summary

**Sobkaj** is a role-based home-service marketplace built as a **Python Flask web application**.  
Its main goal is to connect:

- **Customers** who want to hire service providers
- **Workers** who offer services such as plumbing, electrical work, cleaning, cooking, tutoring, babysitting, etc.
- **Admins** who monitor the platform and view analytics

From a software engineering point of view, this project is a **server-rendered web application** with:

- a **Flask backend**
- a **MySQL relational database**
- a **Jinja2 + HTML/CSS/JavaScript frontend**
- direct SQL queries instead of an ORM

This is a strong **DBMS course project** because it demonstrates:

- relational schema design
- primary key / foreign key relationships
- one-to-one, one-to-many, and many-to-many relationships
- joins, aggregation, subqueries, and filtering
- transactions
- cascading deletes
- seeding scripts
- trigger-based logging

---

## 2. Main Technologies Used

| Layer | Technology | How it is used |
|---|---|---|
| Backend language | Python | Main application logic |
| Web framework | Flask | Routing, request handling, sessions, template rendering |
| Template engine | Jinja2 | Dynamically renders HTML pages with database data |
| Database | MySQL | Stores users, worker profiles, skills, bookings, ratings |
| DB connector | `mysql-connector-python` | Python-to-MySQL communication |
| Frontend structure | HTML | Page layout |
| Frontend styling | CSS + Bootstrap 5 | UI design, responsiveness, reusable components |
| Frontend icons | Bootstrap Icons | Interface icons |
| Frontend scripting | Vanilla JavaScript | OTP boxes, NID verification, some UI interactions |
| Image processing | Pillow | Resizes/crops worker profile photos |
| Password security | Werkzeug security helpers | Password hashing and verification |
| Email | Python `smtplib` + Gmail SMTP | Sends OTP verification emails |
| Deployment | Gunicorn + Procfile | Production WSGI serving |

---

## 3. Project Structure

```text
Sobkaj Last & Final Version (Python Flask)/
├── app.py
├── config.py
├── requirements.txt
├── Procfile
├── backend/
│   ├── __init__.py
│   ├── helpers.py
│   ├── email_utils.py
│   └── routes/
│       ├── __init__.py
│       ├── auth.py
│       ├── customer.py
│       ├── worker.py
│       └── admin.py
├── database/
│   ├── __init__.py
│   ├── db_config.py
│   ├── init_db.sql
│   ├── seed_data.py
│   └── trigger_review_log.sql
└── frontend/
    ├── static/
    │   └── uploads/
    └── templates/
        ├── base.html
        ├── index.html
        ├── login.html
        ├── register.html
        ├── verify_otp.html
        ├── profile_setup.html
        ├── customer_dashboard.html
        ├── customer_profile.html
        ├── my_bookings.html
        ├── leave_review.html
        ├── worker_dashboard.html
        ├── worker_profile.html
        └── admin_dashboard.html
```

### What each folder does

### `backend/`
Contains all Flask-side logic:

- app creation
- utility functions
- email sending
- role-based route handlers

### `database/`
Contains all DB-related code and scripts:

- database connection logic
- schema creation SQL
- seed/demo data
- trigger example

### `frontend/templates/`
Contains all HTML pages rendered by Flask using Jinja2.

### `frontend/static/uploads/`
Stores uploaded worker profile photos after processing.

---

## 4. Overall Architecture

This project follows a **monolithic layered architecture**, not a microservice architecture.

### High-level flow

```text
Browser
  -> Flask route
  -> Python business logic
  -> MySQL query
  -> Result returned to Flask
  -> Jinja2 template rendered
  -> HTML sent back to browser
```

### Real system view

```text
Frontend (HTML/CSS/JS + Bootstrap)
        |
        v
Flask routes (auth / customer / worker / admin)
        |
        v
Helpers + Email Utils + Session Logic
        |
        v
MySQL Database (users, profiles, skills, bookings, ratings)
```

### Important architectural characteristics

- This is **server-side rendered**, not React/Vue/SPA.
- The backend returns full HTML pages for most requests.
- JavaScript is used only for a few interactive pieces:
  - OTP input UX
  - NID verification via `fetch`
  - star rating UI
- There is **no ORM** like SQLAlchemy.
- All SQL is written manually, which is very relevant for a DBMS course.

---

## 5. Application Startup and Boot Process

### Entry point: `app.py`

`app.py` is very small. It imports `create_app()` from `backend/__init__.py` and creates the Flask app object.

### `backend/__init__.py`

This file is the real application bootstrap. It:

1. figures out the base project path
2. creates the Flask app
3. points Flask to the `frontend/templates` and `frontend/static` folders
4. sets the `secret_key`
5. configures the upload folder
6. registers all route modules
7. starts a background thread to initialize the database
8. ensures an admin account exists

### Automatic database initialization

When the app starts, `init_db()` runs in a **background thread**. It:

- opens `database/init_db.sql`
- removes SQL comments
- splits the SQL into statements
- executes the statements one by one
- skips `CREATE DATABASE` and `USE` when appropriate
- updates any old booking commission values to the current rate
- calls `ensure_admin_account()`

This means the app tries to make sure the schema exists every time it starts.

### Why this matters

This design reduces setup friction for demos:

- tables are auto-created
- default skills are auto-inserted
- admin account is auto-synced

---

## 6. Configuration and Environment

### `config.py`

This file stores:

- `PLATFORM_COMMISSION_RATE = 0.05`

So the platform takes a **5% commission** from each booking.

### Database configuration: `database/db_config.py`

The app supports two database modes:

#### Production / cloud mode

If environment variables such as these exist:

- `MYSQL_URL`
- `JAWSDB_URL`

then the app parses the DSN and connects using those values.

#### Local development mode

If cloud variables are not found, it falls back to local MySQL:

- host: `localhost`
- user: `root`
- password: empty
- database: `sobkaj`

### Other environment-driven settings used by the app

- `SECRET_KEY`
- `DEFAULT_ADMIN_EMAIL`
- `DEFAULT_ADMIN_PASSWORD`
- `DEFAULT_ADMIN_NAME`
- `SYNC_ADMIN_ON_STARTUP`

### Production serving

`Procfile` contains:

```text
web: gunicorn app:app
```

So in production, the project expects Gunicorn to serve the Flask app.

---

## 7. Backend Design

The backend is split by feature area.

### `backend/routes/__init__.py`

This file imports and registers route groups:

- authentication routes
- worker routes
- customer routes
- admin routes

### Route organization

| File | Responsibility |
|---|---|
| `backend/routes/auth.py` | registration, OTP, login, logout, landing page |
| `backend/routes/customer.py` | worker browsing, booking, customer profile, booking history, reviews |
| `backend/routes/worker.py` | worker dashboard, profile setup, NID verification, skills, booking status management |
| `backend/routes/admin.py` | admin analytics and user deletion |

### Backend style

This backend is **function-based**, not class-based.

Each file defines a `register_*_routes(app)` function and adds routes directly with `@app.route(...)`.

### Session-based authentication

After successful login, Flask session stores:

- `user_id`
- `full_name`
- `email`
- `role`

The rest of the app uses these session values to determine:

- whether a user is logged in
- which dashboard to show
- whether access is allowed

---

## 8. Frontend Design

The frontend is made with:

- HTML templates
- Jinja2 rendering
- Bootstrap 5
- Bootstrap Icons
- custom inline CSS
- small amounts of vanilla JavaScript

### Important frontend characteristic

This is **not** an API-first frontend.  
Instead, Flask renders ready-made pages on the server and sends them to the browser.

### Base template: `frontend/templates/base.html`

This is the common layout shared by almost all pages. It provides:

- page `<head>`
- Bootstrap imports
- Google Fonts import
- large custom CSS design system
- navbar
- flash messages
- footer
- template blocks for page-specific CSS/JS/content

### Jinja2 templating behavior

The frontend uses Jinja2 expressions like:

- `{{ worker.full_name }}`
- `{% if session.get('role') == 'customer' %}`
- `{% for skill in skills %}`

So the backend sends data into the template context, and Jinja2 decides what appears.

### Frontend pages by purpose

| Template | Purpose |
|---|---|
| `index.html` | marketing landing page |
| `login.html` | login form |
| `register.html` | customer/worker registration form |
| `verify_otp.html` | OTP verification screen |
| `profile_setup.html` | first-time worker profile setup |
| `customer_dashboard.html` | search and browse workers |
| `customer_profile.html` | customer profile editing |
| `my_bookings.html` | customer booking history |
| `leave_review.html` | customer rating/review form |
| `worker_dashboard.html` | worker management dashboard |
| `worker_profile.html` | public worker profile page |
| `admin_dashboard.html` | analytics and user management |

### Frontend JavaScript usage

JavaScript is used for:

- OTP digit boxes with auto-focus and paste support
- countdown display on OTP page
- NID verification using `fetch('/verify_nid')`
- interactive star rating UI
- small UI toggles such as showing worker-specific register fields

This means the project is mostly **SSR + progressive enhancement**.

---

## 9. Database Design

The project uses a **relational MySQL database** with normalized tables.

### Main schema file: `database/init_db.sql`

This file creates the main database objects.

### Tables

#### 1. `users`

Stores all system users:

- customers
- workers
- admins

Important fields:

- `user_id` primary key
- `full_name`
- `email`
- `password_hash`
- `role`
- `phone`
- `created_at`

Important design choice:

- `UNIQUE KEY uq_users_email_role (email, role)`

This means the **same email can exist twice if the roles are different**.  
Example:

- one row for customer account
- one row for worker account

That is why login optionally asks for role.

#### 2. `worker_profiles`

Stores extra data only for workers.

This is a **1:1 relationship** with `users`.

Important fields:

- `profile_id`
- `user_id` unique foreign key
- `nid_number`
- `nid_verified`
- `background_verified`
- `brac_trained`
- `hourly_rate`
- `availability_status`
- `photo_url`
- `bio`

#### 3. `skills`

Stores the catalog of service categories.

Examples:

- Plumber
- Electrician
- Maid
- Babysitter
- Carpenter
- Painter
- Tutor
- Cook

#### 4. `worker_skills`

This is a **junction table** for the many-to-many relationship between workers and skills.

Meaning:

- one worker can have many skills
- one skill can belong to many workers

Composite primary key:

- `(worker_id, skill_id)`

This prevents duplicate worker-skill entries.

#### 5. `bookings`

Stores service bookings between customers and workers.

Important fields:

- `booking_id`
- `customer_id`
- `worker_id`
- `service_date`
- `service_time`
- `hours_requested`
- `total_amount`
- `platform_commission`
- `status`

Booking statuses:

- `pending`
- `confirmed`
- `completed`
- `cancelled`

#### 6. `ratings`

Stores customer ratings after completed bookings.

Important fields:

- `rating_id`
- `booking_id`
- `customer_id`
- `worker_id`
- `stars`
- `review_text`
- `created_at`

Important constraint:

- `CHECK (stars >= 1 AND stars <= 5)`

So the database itself enforces valid star range.

---

## 10. Database Relationships

### Relationship summary

- `users` -> `worker_profiles` = **one-to-one**
- `users` -> `bookings` as customer = **one-to-many**
- `users` -> `bookings` as worker = **one-to-many**
- `users` -> `ratings` as customer = **one-to-many**
- `users` -> `ratings` as worker = **one-to-many**
- `users` <-> `skills` via `worker_skills` = **many-to-many**

### Why this schema is good for a DBMS course

It demonstrates:

- role modeling in one user table
- specialization via profile table
- junction table design
- transaction data table
- feedback table
- aggregation-ready analytics design

### Cascading behavior

Many foreign keys use:

- `ON DELETE CASCADE`
- `ON UPDATE CASCADE`

This means deleting a user can automatically delete related:

- worker profile
- worker skills
- bookings
- ratings

This is especially important in admin deletion.

---

## 11. DBMS Concepts Demonstrated in This Project

This project is more than a CRUD app. It uses many DBMS concepts directly.

### 1. Normalization

Data is split across multiple related tables instead of keeping everything in one huge table.

### 2. Foreign keys

Used to keep relationships valid.

### 3. One-to-one, one-to-many, many-to-many modeling

All three appear clearly in the schema.

### 4. Joins

Used heavily in dashboards and worker listings.

Examples:

- joining `users` with `worker_profiles`
- joining `worker_skills` with `skills`
- joining `bookings` with user names
- joining `ratings` with worker/customer info

### 5. Aggregation

The app uses:

- `AVG`
- `COUNT`
- `SUM`
- `MIN`
- `MAX`
- `ROUND`
- `GROUP_CONCAT`

### 6. Subqueries

Used for:

- checking review counts
- filtering by selected skill
- fetching remaining skills not already assigned

### 7. Transactions

Booking creation explicitly uses:

- `conn.start_transaction()`
- `commit()`
- `rollback()`

This is good DBMS practice because partial booking writes are avoided.

### 8. Trigger example

`database/trigger_review_log.sql` demonstrates an **AFTER INSERT trigger**.

It creates:

- `review_log` table
- `trg_after_review_insert` trigger

Whenever a new rating is inserted, the trigger automatically logs it into `review_log`.

This file is not auto-run, but it is an excellent DBMS concept to discuss in presentation.

### 9. Seed data generation

`database/seed_data.py` creates realistic test/demo data:

- customers
- workers
- worker profiles
- skills
- bookings
- ratings and reviews

This helps produce meaningful analytics on the admin dashboard.

---

## 12. How the Main Features Work

## 12.1 Landing Page

**Route:** `/`

Handled by `backend/routes/auth.py`.

Frontend page:

- `index.html`

Purpose:

- introduce the platform
- show categories
- guide users to register or browse workers

This page is mostly static marketing content rendered through Jinja2.

---

## 12.2 Registration with OTP Verification

### Routes

- `/register`
- `/verify_otp`

### How it works

#### Step 1: user opens registration page

The form lets the user choose:

- customer
- worker

It also collects:

- full name
- email
- phone
- password
- confirm password

#### Step 2: backend validates input

The backend checks:

- required fields
- password confirmation
- role validity
- duplicate `(email, role)` combination

#### Step 3: OTP email is sent

`backend/email_utils.py`:

- generates a random 6-digit OTP
- sends it through Gmail SMTP

#### Step 4: temporary registration data is stored in session

Before OTP verification, the user is **not yet inserted** into the database.  
Instead, the backend stores these in Flask session:

- `reg_full_name`
- `reg_email`
- `reg_phone`
- `reg_password` (already hashed)
- `reg_role`
- `reg_otp`

#### Step 5: user enters OTP

The OTP page uses JavaScript to:

- split input into 6 boxes
- auto-move between boxes
- support paste

#### Step 6: backend verifies OTP

If correct:

- duplicate is checked again
- new user row is inserted into `users`
- registration session values are cleared

### Important architecture point

The OTP is session-based, not database-based.  
So registration is a two-step flow:

```text
Register form -> send OTP -> store pending data in session -> verify OTP -> insert into DB
```

---

## 12.3 Login and Logout

### Routes

- `/login`
- `/logout`

### How login works

The backend:

1. reads email and password
2. optionally reads selected role
3. queries `users`
4. checks password hash using `check_password_hash`
5. stores user information in session
6. redirects based on role

### Role-based redirection

- worker -> `/worker/dashboard`
- admin -> `/admin_dashboard`
- customer -> `/customer/dashboard`

### Special admin handling

Admin login has extra logic:

- default admin credentials can be synced from environment variables
- admin account is auto-created if needed

### Logout

`/logout` simply clears the session.

---

## 12.4 Worker First-Time Profile Setup

### Route

- `/profile_setup`

### Why it exists

Worker registration only creates a user account in `users`.  
It does **not** create `worker_profiles` immediately.

After first login, if no worker profile exists, the user is redirected to profile setup.

### Data collected here

- NID number
- hourly rate
- availability status
- bio
- selected skills
- profile photo

### Backend operations

On submit:

1. NID is checked against a mock in-memory NID dataset
2. photo is processed by Pillow
3. one row is inserted into `worker_profiles`
4. multiple rows are inserted into `worker_skills`

### Why this is important

This separates:

- authentication data (`users`)
- worker-specific data (`worker_profiles`)

which is better relational design.

---

## 12.5 Customer Dashboard: Searching and Browsing Workers

### Route

- `/customer/dashboard`

### What the frontend shows

- search by worker name
- filter by skill
- worker cards
- trust badges
- ratings
- hourly rate
- availability
- booking button

### What the backend does

This route runs a large SQL query joining:

- `users`
- `worker_profiles`
- `worker_skills`
- `skills`
- `ratings`

It uses:

- `GROUP_CONCAT` for worker skills
- `AVG` for average rating
- `COUNT` for rating/review counts
- optional filters for skill and name

### Result

Each worker card is a merged view of profile + skills + rating summary.

This is a very good example of **SQL-driven feature assembly**.

---

## 12.6 Booking a Worker

### Main route

- `/book/<int:worker_id>`

### Who can book

Only logged-in customers.

Backend blocks:

- guests
- workers trying to book
- non-customer roles

### Booking flow

1. customer opens booking modal
2. selects date, time, and hours
3. form submits to Flask
4. backend fetches worker hourly rate
5. backend computes:
   - `total_amount = hourly_rate * hours_requested`
   - `platform_commission = total_amount * 0.05`
6. backend inserts a booking row with status `pending`

### Transaction usage

This route uses a database transaction.  
If any step fails, it rolls back.

### Booking lifecycle

```text
Customer creates booking -> status = pending
Worker accepts -> status = confirmed
Worker finishes -> status = completed
Worker rejects -> status = cancelled
```

---

## 12.7 Customer Booking History

### Route

- `/my_bookings`

### What it shows

- all bookings made by the customer
- worker name
- date/time
- hours
- total cost
- booking status
- whether the customer already reviewed it

### Backend query behavior

The backend joins `bookings` with `users` and uses a subquery to determine if a review exists.

This page is the customer’s transaction history screen.

---

## 12.8 Rating and Reviewing a Worker

### Route

- `/leave_review/<int:booking_id>`

### Rules enforced by backend

- user must be a logged-in customer
- booking must belong to that customer
- booking status must be `completed`
- only one review per booking

### What happens on submission

The backend inserts a row into `ratings` with:

- booking id
- customer id
- worker id
- star value
- optional text review

### Frontend behavior

The review page provides:

- interactive star selection
- rating-only submission
- optional text review

This feature shows a clean relation between:

- bookings
- workers
- customers
- ratings

---

## 12.9 Worker Dashboard

### Route

- `/worker/dashboard`

### What this page contains

- worker profile summary
- NID verification controls
- BRAC training status update
- edit phone/rate/photo
- bio update
- availability update
- skill management
- earnings summary
- rating summary
- incoming bookings

### Backend data sources

This dashboard pulls data from:

- `users`
- `worker_profiles`
- `worker_skills`
- `skills`
- `bookings`
- `ratings`

### Dashboard responsibilities

The worker dashboard acts as a mini control panel for the worker.  
It is where most worker-side operations happen.

---

## 12.10 NID Verification

### Route

- `/verify_nid`

### How it works

This is one of the few AJAX-style features in the project.

Frontend:

- JavaScript sends `FormData` with `nid_number` using `fetch`

Backend:

- checks the number in `DUMMY_NID_DATABASE` inside `backend/helpers.py`
- if found, updates `worker_profiles`
- returns JSON response

### Important note

This is a **mock government verification system**, not a real external API.

That is perfectly acceptable for an academic demo and easy to explain in class.

---

## 12.11 Worker Skill Management

### Routes

- `/add_skill`
- `/remove_skill`

### How it works

Worker skills are stored in `worker_skills`, the junction table.

Adding a skill:

- inserts one `(worker_id, skill_id)` row

Removing a skill:

- deletes one row from `worker_skills`

This is a direct real-world example of **many-to-many relationship management**.

---

## 12.12 Worker Booking Management

### Route

- `/update_booking_status`

### Allowed status changes

- `pending` -> `confirmed`
- `pending` -> `cancelled`
- `confirmed` -> `completed`

### Security check

The SQL update includes:

- the booking id
- the logged-in worker id

So a worker can only update their own bookings.

This is both a business rule and a security measure.

---

## 12.13 Worker Public Profile

### Route

- `/worker/profile/<int:worker_id>`

### What it shows

- worker photo
- name
- skills
- rate
- availability
- trust badges
- bio
- review list

### Backend logic

This route aggregates:

- worker profile data
- concatenated skill list
- average rating
- rating count
- review count
- written reviews

This is the public-facing worker detail page.

---

## 12.14 Customer Profile Editing

### Route

- `/customer/profile`

### What it does

Lets customers update:

- full name
- phone

Email is shown but not editable.

### Database behavior

This only updates the `users` table because customers do not have a separate profile table.

---

## 12.15 Admin Dashboard

### Route

- `/admin_dashboard`

### Purpose

This is the analytics/reporting center of the platform.

### Main sections

#### 1. User statistics

- total users
- total customers
- total workers

#### 2. Revenue statistics

- total completed bookings
- total revenue
- average booking value
- max booking value
- min booking value

#### 3. Commission analytics

- total commission
- earned commission
- pending commission
- commission grouped by booking status

#### 4. Top workers

Ranked using:

- average rating
- completed jobs

#### 5. User management

Lists customers and workers, and allows deletion.

### Why this is strong for presentation

The admin dashboard proves the database is not only storing transactions, but also supporting **analytics and reporting queries**.

---

## 12.16 Admin User Deletion

### Route

- `/admin/delete_user/<int:user_id>`

### How it works

The backend:

1. checks admin session
2. looks up the target user
3. refuses deletion if target is admin
4. deletes the user otherwise

Because of `ON DELETE CASCADE`, related data is also removed automatically.

This demonstrates the practical importance of foreign key cascades.

---

## 13. Helper Modules

## 13.1 `backend/helpers.py`

This file contains shared utility logic.

### Main responsibilities

#### Photo upload handling

- checks file extension
- checks file size
- secures filename
- creates a unique filename using UUID
- uses Pillow to:
  - fix rotation with EXIF
  - convert image mode if needed
  - center-crop to square
  - resize to max `400x400`
  - save as `.webp`

#### Mock NID database

Contains a hardcoded dictionary of sample NID data for demo verification.

#### Schema compatibility helper

`get_background_verification_sql()` detects whether the DB column is:

- `background_verified`
- or older `police_verified`

and returns SQL fragments accordingly.

This is a clever compatibility design for evolving schemas.

---

## 13.2 `backend/email_utils.py`

This file handles:

- OTP generation
- OTP email formatting
- Gmail SMTP sending

### Email flow

1. generate random 6-digit code
2. build HTML email
3. connect to Gmail SMTP with TLS
4. log in
5. send email

---

## 14. Route Summary Table

| Route | Method | Role | Main purpose |
|---|---|---|---|
| `/` | GET | Public | Landing page |
| `/register` | GET/POST | Public | Account registration |
| `/verify_otp` | GET/POST | Public | OTP verification |
| `/login` | GET/POST | Public | Login |
| `/logout` | GET | Logged in users | Logout |
| `/customer/profile` | GET/POST | Customer | Edit customer profile |
| `/customer/dashboard` | GET | Public / Customer | Search workers |
| `/book/<worker_id>` | POST | Customer | Create booking |
| `/my_bookings` | GET | Customer | View bookings |
| `/leave_review/<booking_id>` | GET/POST | Customer | Submit rating/review |
| `/worker/dashboard` | GET | Worker | Worker control panel |
| `/update_booking_status` | POST | Worker | Accept/reject/complete booking |
| `/update_availability` | POST | Worker | Change availability |
| `/update_bio` | POST | Worker | Update bio |
| `/update_worker_profile` | POST | Worker | Update phone/rate/photo |
| `/verify_nid` | POST | Worker | Verify NID via AJAX |
| `/update_brac_training` | POST | Worker | Update BRAC status |
| `/profile_setup` | GET/POST | Worker | First-time profile creation |
| `/add_skill` | POST | Worker | Add skill |
| `/remove_skill` | POST | Worker | Remove skill |
| `/worker/profile/<worker_id>` | GET | Public | Public worker page |
| `/admin_dashboard` | GET | Admin | Analytics dashboard |
| `/admin/delete_user/<user_id>` | POST | Admin | Delete customer/worker |

---

## 15. How Frontend and Backend Interact

This is one of the most important things to understand for presentation.

## 15.1 Most features use normal form submission

Example:

- customer fills booking form
- browser sends POST request
- Flask reads `request.form`
- Flask runs SQL
- Flask sets flash message
- Flask redirects to another page

This is the classic Flask form workflow.

## 15.2 Templates are rendered with data from SQL

Example:

- backend queries workers from MySQL
- passes `workers` list into `render_template("customer_dashboard.html", workers=workers, ...)`
- Jinja2 loops through each worker and renders cards

## 15.3 AJAX is only used selectively

Example:

- NID verification uses `fetch('/verify_nid')`
- backend returns JSON using `jsonify(...)`
- frontend updates part of the page without full reload

So the app is mostly traditional web architecture with one or two AJAX enhancements.

---

## 16. Example Feature Data Flows

## 16.1 Registration flow

```text
User fills register form
-> Flask validates form
-> Duplicate email+role check in users table
-> OTP generated
-> OTP email sent
-> temporary data saved in session
-> user enters OTP
-> Flask verifies OTP
-> new row inserted into users
-> user can now log in
```

## 16.2 Worker booking flow

```text
Customer chooses worker
-> booking form submitted
-> Flask checks logged-in role
-> worker hourly rate loaded from worker_profiles
-> total_amount and platform_commission calculated
-> row inserted into bookings with status='pending'
-> worker sees request in dashboard
-> worker confirms/cancels/completes
```

## 16.3 Review flow

```text
Customer opens completed booking
-> Flask verifies ownership + status='completed'
-> customer submits stars/review
-> row inserted into ratings
-> worker rating statistics change
-> public profile and dashboard show updated summary
```

## 16.4 NID verification flow

```text
Worker enters NID
-> JavaScript sends fetch POST request
-> Flask checks DUMMY_NID_DATABASE
-> if found, worker_profiles updated
-> JSON response returned
-> frontend displays verification result
```

---

## 17. SQL Patterns Used in the Project

This project uses many SQL techniques worth mentioning in class.

### Basic CRUD

- `INSERT INTO users`
- `SELECT ... FROM users`
- `UPDATE worker_profiles`
- `DELETE FROM worker_skills`

### Aggregation

Used in worker dashboards and admin analytics:

- `AVG(r.stars)`
- `COUNT(*)`
- `SUM(total_amount)`

### `GROUP_CONCAT`

Used to convert multiple skill rows into a single comma-separated display string.

### Subqueries

Examples:

- count reviews for each worker
- check if a booking has already been reviewed
- select skills not already owned by a worker

### `FIELD(...)`

Used to sort bookings by status priority in worker dashboard.

### Compatibility-aware SQL

The helper function dynamically adapts query fragments depending on whether the database still has an older verification column name.

---

## 18. Security and Access Control

The project contains several good security-oriented practices.

### Good practices already present

- passwords are stored as **hashes**, not plain text
- session-based login state is used
- many routes check role before allowing access
- workers can only update their own bookings
- admin deletion blocks deletion of admins
- secure filename handling is used for uploads

### Security limitations in current implementation

These are useful to mention honestly in a presentation.

- OTP expiry is mostly session-based; the countdown shown in UI is not strongly enforced server-side
- some secret values have insecure fallbacks
- OTP email credentials are currently coded in Python instead of environment variables
- no CSRF protection library is visible in the current forms

Mentioning these as future improvements shows strong understanding.

---

## 19. Image Upload Pipeline

Worker photo uploads are more advanced than plain file saving.

### Upload process

1. validate extension
2. validate file size
3. create safe unique file name
4. open with Pillow
5. fix orientation
6. crop square
7. resize to thumbnail-style size
8. save as WebP
9. store URL in `worker_profiles.photo_url`

### Why this is good design

- consistent image dimensions
- lower file size
- better visual appearance
- avoids filename collisions

---

## 20. Seeding and Demo Data

### File

- `database/seed_data.py`

### Purpose

Creates realistic demo data so the app looks populated during presentation.

### What it seeds

- 24 customers
- 24 workers
- profiles
- skills
- completed bookings
- future bookings
- ratings
- written reviews

### Why it is useful

Without seed data, admin analytics and ratings pages would look empty.  
With seed data, the teacher can immediately see:

- platform activity
- top workers
- revenue
- commission calculations
- ratings/reviews

### Important detail

This script runs all seed operations inside a **single transaction** and rolls back on failure.

---

## 21. Presentation-Ready Explanation of Each Layer

If your teacher asks, “How do frontend, backend, and database work together?”, you can explain it like this:

### Frontend

The frontend is made of server-rendered HTML templates using Jinja2 and Bootstrap.  
It shows forms, dashboards, modals, search filters, booking lists, and review pages.

### Backend

The backend is Flask. It receives requests, checks session and role, validates form input, performs business logic, runs SQL queries, and returns either HTML pages or JSON responses.

### Database

The database is MySQL. It stores normalized relational data for users, profiles, skills, bookings, and ratings. The backend communicates with it directly using `mysql-connector-python`.

### How they connect

The browser submits a request -> Flask handles it -> Flask queries MySQL -> Flask sends data into Jinja templates -> HTML page is rendered and shown to the user.

---

## 22. What Makes This a Good DBMS Project

This project is not just a website. It clearly demonstrates database-centric concepts:

- relational schema design
- foreign key constraints
- data integrity
- normalized structure
- multi-table joins
- analytics queries
- transaction handling
- trigger example
- seeded test data
- role-based access patterns tied to database records

If your teacher wants the DBMS angle, this is the strongest part to emphasize.

---

## 23. Limitations and Improvement Opportunities

These are not failures. They are useful points for discussion and future development.

### 1. Worker profile booking modal mismatch

The public worker profile page contains a booking form that posts to `/book_worker`, but the backend booking route is `/book/<worker_id>`.  
So booking from that specific modal may not work unless adjusted.

### 2. Registration BRAC checkbox is not persisted

The registration page shows an `is_brac_trained` checkbox for workers, but the registration backend does not currently store that value at registration time. BRAC training is actually updated later from the worker dashboard.

### 3. Driver category appears on landing page but not in DB seed/schema

The homepage shows a “Driver” category link, but the default `skills` table setup does not include a `Driver` skill.

### 4. Upload-size inconsistency

Helper logic and templates mention a 10 MB image limit, but Flask app config currently sets `MAX_CONTENT_LENGTH` to 5 MB. So very large uploads may be blocked earlier than the UI suggests.

### 5. Hardcoded email credentials

The OTP email sender is currently configured directly in code, which is not good production practice. It should be moved to environment variables.

### 6. OTP countdown is mostly frontend UX

The timer displayed on the OTP page is visual; the stronger check is still the session-stored OTP value rather than a persisted database expiry mechanism.

These points are excellent to mention as “future improvements”.

---

## 24. Suggested Improvements for Future Version

- move email credentials fully into environment variables
- add CSRF protection for forms
- unify photo upload limit values
- fix worker public profile booking form route mismatch
- persist OTP expiry timestamp in session or database
- use Flask Blueprints formally for even cleaner structure
- add audit logs for admin actions
- add payment integration
- add real NID verification API integration
- add search by location and availability window
- add unit tests and integration tests

---

## 25. Short Viva / Presentation Script

You can explain the project in this simple way:

> Sobkaj is a Flask-based home-service marketplace. The frontend is built with HTML, Bootstrap, Jinja2, and some JavaScript. The backend is written in Python Flask and is divided into auth, customer, worker, and admin route modules. The database is MySQL and stores normalized relational data in tables like users, worker_profiles, skills, worker_skills, bookings, and ratings. Customers can search workers and create bookings, workers can manage profiles and booking requests, and admins can see analytics like revenue, commission, and top workers. The project also demonstrates core DBMS concepts like joins, aggregation, many-to-many relationships, transactions, cascading deletes, and triggers.

---

## 26. Final Conclusion

Sobkaj is a **full-stack, role-based, database-driven Flask application** where:

- the **frontend** presents forms, dashboards, and dynamic pages
- the **backend** enforces business rules and request handling
- the **database** stores structured relational data and powers both operations and analytics

Technically, it is best understood as:

- a **server-rendered Flask monolith**
- backed by **MySQL**
- using **direct SQL queries**
- designed around **customers, workers, bookings, skills, and ratings**

For a DBMS course presentation, the best strengths to highlight are:

- good relational modeling
- practical joins and analytics
- transaction-based booking insertion
- role-based data flows
- trigger example
- full end-to-end functionality from UI to SQL

