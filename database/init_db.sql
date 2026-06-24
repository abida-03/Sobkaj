-- init_db.sql - creates all the tables Sobkaj needs
-- This runs automatically on app startup through init_db() in backend/__init__.py
-- Using IF NOT EXISTS so it's safe to run multiple times without breaking anything

CREATE DATABASE IF NOT EXISTS sobkaj;
USE sobkaj;

-- main user table - stores customers, workers, and admins
-- the composite unique key (email, role) lets the same email register as both customer and worker
CREATE TABLE IF NOT EXISTS users (
    user_id        INT AUTO_INCREMENT PRIMARY KEY,
    full_name      VARCHAR(100)  NOT NULL,
    email          VARCHAR(150)  NOT NULL,
    password_hash  VARCHAR(255)  NOT NULL,
    role           ENUM('customer', 'worker', 'admin') NOT NULL,
    phone          VARCHAR(20),
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_users_email_role (email, role)
) ENGINE=InnoDB;

-- extra profile info for workers (1:1 with users via UNIQUE user_id)
-- ON DELETE CASCADE means deleting a user auto-deletes their profile too
CREATE TABLE IF NOT EXISTS worker_profiles (
    profile_id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id             INT NOT NULL UNIQUE,
    nid_number          VARCHAR(50),
    nid_verified        BOOLEAN DEFAULT FALSE,
    background_verified BOOLEAN DEFAULT FALSE,
    brac_trained        BOOLEAN DEFAULT FALSE,
    hourly_rate         DECIMAL(10, 2) DEFAULT 0.00,
    availability_status ENUM('available', 'busy', 'offline') DEFAULT 'available',
    photo_url           VARCHAR(500),
    bio                 TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- list of service categories workers can register for
CREATE TABLE IF NOT EXISTS skills (
    skill_id    INT AUTO_INCREMENT PRIMARY KEY,
    skill_name  VARCHAR(100) NOT NULL UNIQUE,
    description TEXT
) ENGINE=InnoDB;

-- junction table for the many-to-many relationship between workers and skills
-- composite primary key (worker_id, skill_id) prevents duplicate entries
CREATE TABLE IF NOT EXISTS worker_skills (
    worker_id  INT NOT NULL,
    skill_id   INT NOT NULL,
    PRIMARY KEY (worker_id, skill_id),
    FOREIGN KEY (worker_id) REFERENCES users(user_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (skill_id)  REFERENCES skills(skill_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- each booking links a customer to a worker for a specific date and time
-- two foreign keys point to the same users table (customer_id and worker_id)
CREATE TABLE IF NOT EXISTS bookings (
    booking_id          INT AUTO_INCREMENT PRIMARY KEY,
    customer_id         INT NOT NULL,
    worker_id           INT NOT NULL,
    service_date        DATE NOT NULL,
    service_time        TIME DEFAULT '09:00:00',
    hours_requested     DECIMAL(4, 2) NOT NULL,
    total_amount        DECIMAL(10, 2) DEFAULT 0.00,
    platform_commission DECIMAL(10, 2) DEFAULT 0.00,
    status              ENUM('pending', 'confirmed', 'completed', 'cancelled')
                            DEFAULT 'pending',
    FOREIGN KEY (customer_id) REFERENCES users(user_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (worker_id) REFERENCES users(user_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- customers rate workers after a booking is completed (1-5 stars + optional text)
-- CHECK constraint ensures stars stay between 1 and 5
CREATE TABLE IF NOT EXISTS ratings (
    rating_id   INT AUTO_INCREMENT PRIMARY KEY,
    booking_id  INT NOT NULL,
    customer_id INT NOT NULL,
    worker_id   INT NOT NULL,
    stars       INT NOT NULL CHECK (stars >= 1 AND stars <= 5),
    review_text TEXT,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id)  REFERENCES bookings(booking_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES users(user_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (worker_id)   REFERENCES users(user_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- pre-populate the skill catalog so workers can pick from these during signup
INSERT IGNORE INTO skills (skill_name, description) VALUES
    ('Plumber',      'Fixes pipes, faucets, and drainage systems'),
    ('Electrician',  'Handles wiring, electrical repairs, and installations'),
    ('Maid',         'Provides cleaning and household maintenance services'),
    ('Babysitter',   'Takes care of children in the absence of parents'),
    ('Carpenter',    'Builds and repairs wooden structures and furniture'),
    ('Painter',      'Paints walls, ceilings, and exterior surfaces'),
    ('Tutor',        'Provides academic tutoring and homework help'),
    ('Cook',         'Prepares meals and manages kitchen duties');
