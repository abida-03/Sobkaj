# Sobkaj - Home Service Marketplace Platform

A role-based home-service marketplace built with **Python Flask**, **MySQL**, and **HTML/CSS/JavaScript**. Sobkaj connects customers with qualified service workers for services like plumbing, electrical work, cleaning, cooking, tutoring, and more.

## 🎯 Project Overview

**Sobkaj** is a comprehensive demonstration of database design and web application architecture. It's an excellent **DBMS course project** showcasing relational database concepts, normalization, relationships, transactions, and SQL queries in a real-world application context.

### Key Users

- **Customers** - Browse workers, book services, leave reviews
- **Workers** - Manage profiles, accept bookings, build reputation
- **Admins** - Monitor platform analytics and manage users

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend** | Python Flask | Web framework & routing |
| **Database** | MySQL | Relational data storage |
| **Frontend** | HTML5 + Jinja2 | Server-rendered templates |
| **Styling** | Bootstrap 5 + CSS | Responsive UI design |
| **Icons** | Bootstrap Icons | Interface iconography |
| **Database Connector** | mysql-connector-python | Python-MySQL communication |
| **Image Processing** | Pillow | Profile photo resizing |
| **Security** | Werkzeug | Password hashing & verification |
| **Email** | smtplib + Gmail SMTP | OTP verification emails |
| **Production Server** | Gunicorn + Procfile | WSGI application serving |

## 📁 Project Structure

```
Sobkaj/
├── app.py                          # Application entry point
├── config.py                       # Configuration settings (commission rates, etc.)
├── requirements.txt                # Python dependencies
├── Procfile                        # Production deployment config
├── Overview.md                     # Detailed project documentation
├── backend/
│   ├── __init__.py                # App factory & initialization
│   ├── helpers.py                 # Utility functions
│   ├── email_utils.py             # OTP email sending
│   └── routes/
│       ├── auth.py                # Authentication & registration
│       ├── customer.py            # Customer features (booking, reviews)
│       ├── worker.py              # Worker profile & management
│       └── admin.py               # Admin analytics & controls
├── database/
│   ├── db_config.py               # Database connection management
│   ├── init_db.sql                # Schema & table creation
│   ├── seed_data.py               # Demo data generation
│   └── trigger_review_log.sql     # Database trigger example
└── frontend/
    ├── templates/                 # Jinja2 HTML templates
    │   ├── base.html              # Base layout template
    │   ├── index.html             # Landing page
    │   ├── login.html             # Login form
    │   ├── register.html          # Registration form
    │   ├── verify_otp.html        # OTP verification
    │   ├── profile_setup.html     # Worker profile setup
    │   ├── customer_dashboard.html # Worker browsing & search
    │   ├── worker_dashboard.html  # Worker control panel
    │   ├── admin_dashboard.html   # Analytics & user management
    │   └── ... other pages
    └── static/uploads/            # User-uploaded profile photos
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- MySQL Server (local or cloud)
- Gmail account (for OTP emails)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/abida-03/Sobkaj.git
   cd Sobkaj
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure database connection**
   
   For **local development**:
   - Ensure MySQL is running with user `root` (no password)
   - Create database: `CREATE DATABASE sobkaj;`
   
   For **production/cloud** (JawsDB, etc.):
   - Set environment variable: `MYSQL_URL` or `JAWSDB_URL`

4. **Set up environment variables**
   ```bash
   export SECRET_KEY="your-secret-key"
   export DEFAULT_ADMIN_EMAIL="admin@example.com"
   export DEFAULT_ADMIN_PASSWORD="admin123"
   ```

5. **Run the application**
   ```bash
   python app.py
   ```
   
   The app will auto-initialize the database on startup.

6. **Access the application**
   - Open your browser: `http://localhost:5000`
   - Landing page loads automatically
   - Register as customer or worker to get started

## 💡 Core Features

### 🔐 Authentication & Registration
- Email verification with OTP
- Role-based login (customer/worker/admin)
- Secure password hashing using Werkzeug
- Session-based authentication

### 👥 Customer Features
- **Browse Workers** - Search and filter by skill with ratings
- **Book Services** - Select date, time, and hours
- **My Bookings** - View booking history and status
- **Leave Reviews** - Rate and review completed bookings
- **Profile Management** - Update customer information

### 🔧 Worker Features
- **Profile Setup** - Add bio, hourly rate, skills, and photo
- **NID Verification** - Government ID verification (mock)
- **Skill Management** - Add/remove service categories
- **Booking Dashboard** - Accept/manage incoming bookings
- **Earnings & Ratings** - View performance metrics and reviews

### 📊 Admin Features
- **Platform Analytics** - Revenue, bookings, user counts
- **User Management** - View and remove users
- **Commission Tracking** - 5% platform commission calculation
- **System Oversight** - Monitor all transactions

## 🗄️ Database Design

### Core Tables

| Table | Purpose | Relationships |
|-------|---------|---------------|
| `users` | All system users (customers, workers, admins) | Primary entity |
| `worker_profiles` | Worker-specific data (NID, rate, bio) | 1:1 with users |
| `skills` | Service categories (Plumber, Electrician, etc.) | Referenced by workers |
| `worker_skills` | Many-to-many: workers ↔ skills | Junction table |
| `bookings` | Service bookings between customers & workers | Foreign keys to users |
| `ratings` | Customer reviews after completed bookings | Foreign keys to bookings & users |

### Key DBMS Concepts Demonstrated

✅ **Normalization** - Properly split data across related tables  
✅ **Relationships** - One-to-one, one-to-many, many-to-many  
✅ **Foreign Keys** - Referential integrity constraints  
✅ **Joins** - Complex multi-table queries  
✅ **Aggregation** - AVG, COUNT, SUM, GROUP_CONCAT  
✅ **Subqueries** - Nested queries for filtering  
✅ **Transactions** - ACID guarantees for bookings  
✅ **Triggers** - Automatic logging on review insertion  
✅ **Cascading Deletes** - Maintain data consistency  

## 🔄 Main Workflows

### Registration & OTP Flow
```
Register form → Generate OTP → Send email → Store in session 
→ User verifies OTP → Create user in database
```

### Booking Workflow
```
Customer searches workers → Selects worker & date/time 
→ System calculates cost with commission → Creates pending booking 
→ Worker accepts/rejects → Status updated → Customer can review when completed
```

### Rating System
```
Completed booking → Customer clicks "Leave Review" 
→ Submits 1-5 stars + optional text → Rating inserted into database 
→ Worker's average rating updated
```

## ⚙️ Configuration

### Platform Settings (`config.py`)
```python
PLATFORM_COMMISSION_RATE = 0.05  # 5% commission on all bookings
```

### Database Configuration (`database/db_config.py`)
- **Local**: `localhost`, user `root`, database `sobkaj`
- **Cloud**: Parses `MYSQL_URL` or `JAWSDB_URL` environment variables

### Environment Variables
- `SECRET_KEY` - Flask session secret
- `MYSQL_URL` / `JAWSDB_URL` - Cloud database URL
- `DEFAULT_ADMIN_EMAIL` - Admin account email
- `DEFAULT_ADMIN_PASSWORD` - Admin account password
- `SYNC_ADMIN_ON_STARTUP` - Auto-create/update admin on boot

## 🏗️ Application Architecture

### Architecture Pattern
**Server-Side Rendered (SSR) Monolith** - Not an API-first SPA

### Request Flow
```
Browser
  ↓
Flask Route Handler
  ↓
Python Business Logic
  ↓
MySQL Database Query
  ↓
Result → Jinja2 Template Rendering
  ↓
HTML Page → Browser
```

### Backend Organization
- **Function-based views** (not class-based)
- **Route modules** for each feature area (auth, customer, worker, admin)
- **Session-based authentication** using Flask sessions
- **Direct SQL** instead of ORM (great for learning SQL!)

### Frontend Approach
- **Jinja2 templates** for dynamic HTML rendering
- **Bootstrap 5** for responsive design
- **Vanilla JavaScript** for interactive elements:
  - OTP input boxes with auto-focus
  - NID verification via `fetch()`
  - Star rating UI
  - Form validation

## 🔐 Security Features

- **Password Hashing** - Werkzeug security helpers
- **Session Management** - Secure Flask sessions
- **Email Verification** - OTP-based registration
- **Role-Based Access Control** - Different dashboards per role
- **SQL Injection Protection** - Parameterized queries
- **CSRF Protection** - Built-in with Flask

## 🌍 Deployment

### Production Deployment
The project includes a `Procfile` for cloud deployment:
```
web: gunicorn app:app
```

### Supported Platforms
- **Heroku** - Via Procfile
- **Azure** - With JawsDB MySQL
- **Any cloud with Gunicorn support**

### Environment Setup
1. Set all required environment variables on the cloud platform
2. Ensure MySQL database is accessible via `JAWSDB_URL` or `MYSQL_URL`
3. Deploy using your platform's deployment method
4. Database initializes automatically on first run

## 📚 Learning Outcomes

This project is ideal for learning:

- **Database Design** - Relational schema design with normalization
- **SQL Queries** - Joins, aggregation, subqueries, transactions
- **Web Development** - Flask, routing, templating, sessions
- **Full-Stack Development** - Frontend to database integration
- **Authentication** - User registration, verification, role-based access
- **Real-World Design Patterns** - Booking systems, rating systems, transactions

## 📝 Additional Documentation

See **`Overview.md`** for comprehensive technical documentation including:
- Detailed database schema descriptions
- All route documentation
- Feature workflows
- DBMS concepts demonstrated
- Frontend JavaScript examples
- Email template details
- Troubleshooting guide

## 🤝 Contributing

This is a course project. Contributions for educational improvements are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is for educational purposes.

## 👤 Author

Created by **abida-03**

---

**Ready to get started?** Clone the repo and follow the Getting Started section above. The application will auto-initialize your database!